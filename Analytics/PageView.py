from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from pymongo.collection import Collection

from utils.MongoBase import MongoBase


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
        return self._query.get("docid", [None])[0]

    @property
    def context(self):
        return self._query.get("context", [None])[0]

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
        """
            Store this page view to MonogoDB
            Args:
                views (Collection) : list of views from Google Analytics
            Returns:

        """
        views.insert_one(self.mongo_representation)

    @property
    def mongo_representation(self):
        """
            Create this page view object to store in MonogoDB
            Returns:
                Page View json object
        """
        return {
            "doc_id": self.doc_id,
            "context": self.context,
            "city": self.city,
            "country": self.country,
            "count": self._count,
            "at": self.when
        }

    @MongoBase.with_book_collection
    def get_book(self, books: Collection):
        return books.find_one(self.doc_id)

    def exists(self):
        """
            Look for matching views in the last minute
            Returns:
                True if the view exists in last minute
                False if not
        """
        return MongoBase.get_view_collection().aggregate([{
            "$match": {
                "$and": [
                    {"doc_id": {"$eq": self.doc_id}},
                    {"city": {"$eq": self.city}},
                    {"country": {"$eq": self.country}},
                    {"at": {"$lt": self.when - timedelta(minutes=1)}},
                ]
            }
        }]) is not None
