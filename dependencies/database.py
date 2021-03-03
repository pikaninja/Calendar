import asyncio
import datetime
import functools
from typing import Any, Coroutine, Dict, List, Optional, Tuple

import asyncpg
from asyncpg.pool import Pool

from .objects import Container, MemberProxy, Reminder, Settings
from utils.errors import DuplicateGroup


class Database:
    def connect(coro: Coroutine):
        @functools.wraps(coro)
        async def predicate(self, *args, **params):
            await self.wait_until_loaded()

            async with self.pool.acquire() as conn:
                return await coro(self, conn, *args, **params)
        return predicate

    def __init__(self, **config):
        self.config = config

        self._loaded = asyncio.Event()
        self.pool: Pool = None
        self.groups: Dict[int, Tuple[int]] = None
        self.members: Dict[int, int] = None
        self.settings: Dict[int, Dict[str, Any]] = None
        self.reminders: Dict[int, List[Reminder]] = None
        self.loop = asyncio.get_event_loop()

        self.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.config)
        self.groups = []
        self.members = {}
        self.settings = Container()
        self.reminders = Container()

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA calendar;

                CREATE TABLE IF NOT EXISTS calendar.groups(
                    id SERIAL PRIMARY KEY,
                    member_ids BIGINT[10] NOT NULL
                );

                CREATE TABLE IF NOT EXISTS calendar.members(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS calendar.settings(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT,
                    group_id BIGINT,
                    utc_offset SMALLINT DEFAULT 0,
                    dark_mode BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS calendar.reminders(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT,
                    group_id BIGINT,
                    timestamp TIMESTAMP NOT NULL,
                    event VARCHAR(1000)
                );
            """)

            await self._init_cache(conn)
        self._loaded.set()

    async def _init_cache(self, conn):
        # have mercy on my soul
        groups = await conn.fetch("SELECT * FROM calendar.groups;")
        members = await conn.fetch("SELECT * FROM calendar.members;")
        settings = await conn.fetch("SELECT * FROM calendar.settings;")
        reminders = await conn.fetch("SELECT * FROM calendar.reminders;")

        for _id, member_ids in groups:
            self.groups[_id] = set(member_ids)

        for _id, member_id in members:
            groups = self.find_groups(member_id)
            self.members[member_id] = MemberProxy(_id, member_id, groups)

        for _id, member_id, group_id, *args in settings:
            select_id = member_id
            which = self.settings.users

            if not member_id:
                select_id = group_id
                which = self.settings.groups
            which[select_id] = Settings(_id, select_id, *args)

        for _id, member_id, group_id, *args in reminders:
            select_id = member_id
            which = self.reminders.users

            if not member_id:
                select_id = group_id
                which = self.reminders.groups
            reminders_obj = which.setdefault(select_id, [])
            index = len(reminders_obj)
            obj = Reminder(_id, index, *args)

            reminders_obj.append(obj)

    def _get_next_index(self,
                        *, member_id: Optional[int] = None,
                        group_id: Optional[int]):
        if member_id:
            return len(self.reminders.setdefault(member_id, {}))
        elif group_id:
            group_reminders = self.reminders["_group"]

            return len(group_reminders.setdefault(group_id, {}))
        raise ValueError("no ID passed into relevant kwargs")

    def _invalidate_group(self, *member_ids):
        return False

    def _resolve_group_id(self, _id: int):
        group_reminders = self.reminders["_group"]
        return group_reminders.get(_id, None)

    def find_groups(self, member_id: int):
        groups = {}

        for _id, group_members_ids in self.groups.items():
            if member_id in group_members_ids:
                groups[_id] = set(group_members_ids)
        return groups

    async def wait_until_loaded(self):
        await self._loaded.wait()

    async def close(self):
        await self.pool.close()

    @connect
    async def _get_internal_id(self, conn, member_id: int):
        internal_id = self.members.get(member_id, None)

        if not internal_id:
            internal_id = self.members[member_id] = await conn.fetchval(
                "INSERT member_id INTO members VALUES($1) RETURNING id;",
                member_id
            )
        return internal_id

    @connect
    async def create_group(self, conn, *member_ids):
        # (L82) requires duplicate validation
        existing_group = self._invalidate_group(*member_ids)

        if existing_group:
            raise DuplicateGroup(existing_group)
        values = []

        for i in range(1, len(member_ids) + 1):
            values = f"${i}"
        joined = (", ").join(values)

        _id = await conn.execute(
            f"INSERT INTO groups VALUES({joined}) RETURNING id;",
            *member_ids
        )
        self.groups[_id] = member_ids

    @connect
    async def add_reminder(self,
                           conn,
                           select_id: int,
                           timestamp: datetime.datetime,
                           event: Optional[str] = None):
        id_param = "member_id"
        which = self.reminders
        group_found = self._resolve_group_id(select_id)

        if group_found:
            id_param = "group_id"
            which = group_found
        args = [select_id, timestamp, event]
        query = f"""
            INSERT INTO reminders({id_param}, timestamp, event)
            VALUES($1, $2, $3) RETURNING id;
        """
        kwargs = {id_param: select_id}
        index = self._get_next_index(**kwargs)
        _id = await conn.execute(query, *args)
        obj = Reminder(_id, index, timestamp, event, group=group_found)

        which.append(obj)

    @connect
    async def pop_reminder(self, conn, member_id: int, index: int):
        reminders = self._get_member_reminders(member_id)

        if not reminders or index > len(reminders):
            return None
        reminder = reminders.pop(index)

        await conn.execute("DELETE FROM reminders WHERE id=$1;", reminder.id)
        return reminder


def create(**config):
    return Database(**config)
