from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from pymongo.collection import Collection

from Models.MongoBase import MongoBase


@dataclass
class PageView:
    path: str
    minutes_ago: str
    country: str
    city: str
    page_title: str
    count: str

    @property
    def _query(self) -> dict:
        path = urlparse(self.path)
        return parse_qs(path.query)

    @property
    def doc_id(self):
        return self._query.get("docid", None)

    @property
    def context(self):
        return self._query.get("context", None)

    @property
    def _minutes_ago(self):
        return int(self.minutes_ago)

    @property
    def _count(self):
        return int(self.count)

    @property
    def when(self):
        return datetime.now() - timedelta(minutes=self._minutes_ago)

    @MongoBase.with_view_collection
    def store(self, views: Collection):
        views.insert_one({
            "doc_id": self.doc_id,
            "context": self.context,
            "city": self.city,
            "country": self.country,
            "time": self.when
        })
