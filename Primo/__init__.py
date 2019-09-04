import os

import requests
from celery import Celery
from pymongo.collection import Collection

from utils.MongoBase import MongoBase
from Primo.transform import transform


@MongoBase.with_book_collection
def book_exists(doc_id: str, books: Collection):
    return books.find_one(doc_id) is not None


def get_book(doc_id: str, context: str):
    api_key = os.getenv("PRIMO_API_KEY")
    primo_pnx_gateway = os.getenv("PRIMO_PNX_GATEWAY")

    url = f"{primo_pnx_gateway}/{context}/{doc_id}"

    querystring = {"apiKey": api_key}

    payload = ""
    headers = {
        'accept': "application/json"
    }

    response = requests.get(url, data=payload, headers=headers, params=querystring)

    return response.json()


@MongoBase.with_book_collection
def store_record(record: dict, books: Collection):
    insert = books.insert_one(record)
    return insert.inserted_id
