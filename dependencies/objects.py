import datetime
from typing import Dict, Iterable, Optional


class Reminder:
    def __init__(self,
                 _id: int,
                 index: int,
                 timestamp: datetime.datetime,
                 event: Optional[str] = "",
                 *, group: Optional[Dict]):
        self.id = _id
        self.index = index
        self.timestamp = timestamp
        self.event = event
        self.group = group

    @property
    def late(self):
        return datetime.datetime.now() > self.timestamp

    @property
    def delta(self):
        return self.timestamp - datetime.datetime.now()

    @property
    def diff(self):
        return self.delta.total_seconds()

    @property
    def member_ids(self):
        if not self.group:
            return None
        ret = set()

        for ids in self.group.values():
            for _id in ids:
                ret.add(_id)
        return ret


class MemberProxy:
    def __init__(self, row_id: int, _id: int, groups: Optional[Dict[int, Iterable[int]]]):
        self.row_id = row_id
        self.id = _id
        self.groups = None

        if groups:
            self.groups = groups
