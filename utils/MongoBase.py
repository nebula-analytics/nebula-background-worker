import inspect

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from utils import receives_config


class MongoBase:
    __client: MongoClient = None

    @classmethod
    @receives_config("database")
    def _get_client(cls, config):
        if cls.__client is None:
            auth_string = ""
            if config.mongodb.username:
                auth_string = f"{config.mongodb.username}:{config.mongodb.password}@"
            cls.__client = pymongo.MongoClient(
                f"mongodb://{auth_string}{config.mongodb.host}")

        """ Test Connection """
        try:
            cls.__client.admin.command('ismaster')
        except ConnectionFailure:
            raise

        return cls.__client

    @classmethod
    @receives_config("database")
    def _get_database(cls, config):
        client = cls._get_client()
        database = client[config.mongodb.database]
        return database

    @classmethod
    @receives_config("database")
    def get_view_collection(cls, config):
        return cls._get_database().get_collection(config.mongodb.collections.views)

    @classmethod
    @receives_config("database")
    def get_book_collection(cls, config):
        return cls._get_database().get_collection(config.mongodb.collections.books)

    @classmethod
    @receives_config("database")
    def get_util_collection(cls, config):
        return cls._get_database().get_collection(config.mongodb.collections.utils)

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
    @receives_config("database")
    def with_view_collection(cls, fn, database=None):
        return cls._with_collection(database.mongodb.collections.views, fn)

    @classmethod
    @receives_config("database")
    def with_book_collection(cls, fn, database=None):
        return cls._with_collection(database.mongodb.collections.books, fn)

    @classmethod
    @receives_config("database")
    def with_utils_collection(cls, fn, database=None):
        return cls._with_collection(database.mongodb.collections.utils, fn)
