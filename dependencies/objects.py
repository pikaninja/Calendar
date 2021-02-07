import datetime
from typing import Optional


class Reminder:
    def __init__(self,
                 _id: int,
                 index: int,
                 timestamp: datetime.datetime,
                 event: Optional[str] = ""):
        self.id = _id
        self.index = index
        self.timestamp = timestamp
        self.event = event

    @property
    def late(self):
        return datetime.datetime.now() > self.timestamp

    @property
    def diff(self):
        return self.timestamp - datetime.datetime.now()
