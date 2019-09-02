import os
import time
from threading import Thread
from typing import Callable

from argument_parser import receive_arguments
from authentication import GAuth

import requests


def start():
    while True:
        t = Thread(target=update, args=(add_view,))
        t.start()
        time.sleep(10)


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


def add_view(document: dict):
    """
    1. Check document doc_id is in books
    2. If it isn't request book info from primo
    3. Add primo data to books
    :param document:
    :return:
    """
    print(document)


@GAuth.require("analytics", "v3")
@receive_arguments
def update(view_callback: Callable, analytics, view_id):
    """
    1. Retrieve analytics
    2. Call add_view on each view

    :return:
    """
    result = analytics.data().realtime().get(
        ids=f"ga:{view_id}",
        metrics='rt:pageviews',
        dimensions='rt:pagePath,rt:minutesAgo,rt:country,rt:city,rt:pageTitle',
        filters=r"rt:pagePath=~/primo-explore/.*docid.*",
        sort="rt:minutesAgo"
    ).execute()

    rows = result["rows"]
    for row in rows:
        view_callback(row)


"""
{
    "views": [
        {
            "doc_id": "RMIT_ALMA_123",
            "seen": "01/01/2019T10:01:12+1211",
            "country": "Australia",
            "city": "Melbourne",
        }
    ],
    "books": [
        {
            "doc_id": "RMIT_ALMA_123",
            "thumbnail": "",
            "title": "",

        }
    ]
}
"""
