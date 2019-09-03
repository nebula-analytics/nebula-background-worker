import inspect
import os

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MongoBase:
    DATABASE = os.getenv("DATABASE_NAME", "nebula")
    VIEW_COLLECTION = os.getenv("VIEW_COLLECTION_NAME", "views")
    BOOK_COLLECTION = os.getenv("BOOK_COLLECTION_NAME", "books")
    HOST = os.getenv("MONGO_HOST", "mongodb://localhost:27017/")
    __client: MongoClient = None

    @classmethod
    def _get_client(cls):

        if cls.__client is None:
            cls.__client = pymongo.MongoClient(cls.HOST)

        """ Test Connection """
        try:
            cls.__client.admin.command('ismaster')
        except ConnectionFailure:
            raise

        return cls.__client

    @classmethod
    def _get_database(cls):
        client = cls._get_client()
        database = client[cls.DATABASE]
        return database

    @classmethod
    def get_view_collection(cls):
        return cls._get_database().get_collection(cls.VIEW_COLLECTION)

    @classmethod
    def get_book_collection(cls):
        return cls._get_database().get_collection(cls.BOOK_COLLECTION)

    @classmethod
    def _with_collection(cls, name, fn):
        def wrapper(*args, **kwargs):
            db = cls._get_database()
            kwargs[name] = db.get_collection(name)
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        wrapper.__signature__ = inspect.signature(fn)
        return wrapper

    @classmethod
    def with_view_collection(cls, fn):
        return cls._with_collection(cls.VIEW_COLLECTION, fn)

    @classmethod
    def with_book_collection(cls, fn):
        return cls._with_collection(cls.BOOK_COLLECTION, fn)
