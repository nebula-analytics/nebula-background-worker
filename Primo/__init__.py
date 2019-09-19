import requests
from pymongo.collection import Collection

from Primo.transform import transform
from utils import receives_config, ConfigMap
from utils.MongoBase import MongoBase


@MongoBase.with_book_collection
def book_exists(doc_id: str, books: Collection):
    """
        Args:
            doc_id (str): doc_id of a document in Primo Database
            books (Collection): list of books from Mongo Database
        Raises:
        Returns:
            True if exists a book having match doc_id in Mongo Database
            False if not
    """
    return books.find_one({"doc_id": doc_id}) is not None


@receives_config("primo")
def get_book(doc_id: str, context: str, primo: ConfigMap):
    """
    Retrieve book information from Primo
        Args:
            doc_id (str): doc_id of a document in Primo Database
            context (str): Primo context, L or PC
        Raises:
        Returns:
            tuple of json for book information and status code of response
    """
    api_key = primo.api_key
    primo_pnx_gateway = primo.host

    url = f"{primo_pnx_gateway}/{context}/{doc_id}"

    querystring = {"apiKey": api_key}

    payload = ""
    headers = {
        'accept': "application/json"
    }

    response = requests.get(url, data=payload, headers=headers, params=querystring, verify=False)

    return response.json(), response.status_code


def update_record(_id: str, **record):
    """
    update record of books collection in MongoDB
        Args:
            _id (str): doc_id of a document in Primo Database
            record : new record
        Raises:
        Returns:
            The _id of the inserted document if an upsert took place. Otherwise ``None``.
    """
    books = MongoBase.get_book_collection()
    result = books.update_one({
        "doc_id": _id
    }, {
        "$set": record
    })
    return result.upserted_id
