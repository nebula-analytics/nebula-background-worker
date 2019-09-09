import requests
from pymongo.collection import Collection

from Primo.transform import transform
from utils import receives_config, ConfigMap
from utils.MongoBase import MongoBase


@MongoBase.with_book_collection
def book_exists(doc_id: str, books: Collection):
    return books.find_one({"doc_id": doc_id}) is not None


@receives_config("primo")
def get_book(doc_id: str, context: str, primo: ConfigMap):
    api_key = primo.api_key
    primo_pnx_gateway = primo.host

    url = f"{primo_pnx_gateway}/{context}/{doc_id}"

    querystring = {"apiKey": api_key}

    payload = ""
    headers = {
        'accept': "application/json"
    }

    response = requests.get(url, data=payload, headers=headers, params=querystring)

    return response.json(), response.status_code


def update_record(_id: str, **record):
    books = MongoBase.get_book_collection()
    result = books.update_one({
        "doc_id": _id
    }, {
        "$set": record
    })
    return result.upserted_id
