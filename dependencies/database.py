import asyncio
import datetime
import functools
from typing import Coroutine, Dict, List, Optional

import asyncpg
from asyncpg.pool import Pool

from .objects import Reminder


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
        self.members: Dict[int, int] = {}
        self.reminders: Dict[int, List[Reminder]] = {}
        self.loop = asyncio.get_event_loop()

        self.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.config)

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS members(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reminders(
                    id SERIAL PRIMARY KEY,
                    member_id BIGINT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    event VARCHAR(1000)
                );
            """)

            members = await conn.fetch("SELECT * FROM members;")
            reminders = await conn.fetch("SELECT * FROM reminders;")

            for _id, member_id in members:
                self.members[member_id] = _id

            for _id, member_id, *args in reminders:
                members_reminders = self.reminders.setdefault(member_id, [])
                index = len(members_reminders)
                obj = Reminder(_id, index, *args)

                members_reminders.append(obj)
        self._loaded.set()

    def _get_member_reminders(self, member_id: int):
        return self.reminders.setdefault(member_id, {})

    @connect
    async def _get_member_serial(self, conn, member_id: int):
        serial_found = self.members.get(member_id, None)

        if not serial_found:
            serial_found = self.members[member_id] = await conn.fetchval(
                "INSERT member_id INTO members VALUES($1) RETURNING id;",
                member_id
            )
        return serial_found

    @connect
    async def add_reminder(self,
                           conn,
                           member_id: int,
                           timestamp: datetime.datetime,
                           event: Optional[str] = None):
        reminders = self._get_member_reminders(member_id)
        index = len(reminders)
        member_serial = await self._get_member_serial(member_id)

        _id = await conn.execute(
            """
                INSERT INTO reminders(member_id, timestamp, event)
                VALUES($1, $2, $3) RETURNING id;
            """,
            member_serial,
            timestamp,
            event
        )
        obj = Reminder(_id, index, timestamp, event)

        reminders.append(obj)

    @connect
    async def pop_reminder(self, conn, member_id: int, index: int):
        reminders = self._get_member_reminders(member_id)

        if not reminders or index > len(reminders):
            return None
        reminder = reminders.pop(index)

        await conn.execute("DELETE FROM reminders WHERE id=$1;", reminder.id)
        return reminder

    @connect
    async def drop(self, conn):
        self._loaded.clear()
        await conn.execute("DROP TABLE members, reminders;")
        await self.loop.create_task(self.__ainit__())

    async def wait_until_loaded(self):
        await self._loaded.wait()

    async def close(self):
        await self.pool.close()


def create(**config):
    return Database(**config)
