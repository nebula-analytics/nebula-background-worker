from datetime import datetime
from math import ceil
from typing import Optional, Union

from celery import Celery
from celery_once import QueueOnce

from Analytics.PageView import PageView
from Analytics.helpers import generate_view_rows
from Primo import *
from Primo.transform import transform
from utils import receives_config

app = Celery("schedule")

receives_config("celery", as_json=True)(app.config_from_object)()


@app.task(base=QueueOnce, once={"graceful": True})
def request_record(doc_id: str, context: str, attempted_contexts=()) -> Optional[Union[str, dict]]:
    """
    Request a primo record
    This task should be rate limited
    :param attempted_contexts:
    :param doc_id: The primo doc_id
    :param context: The primo context, L or PC
    :return: The primo response
    """
    primo = ConfigMap.get_singleton().primo

    if book_exists(doc_id):
        return print(f"[{doc_id}, {context}] Book exists, aborting")

    book, status = get_book(doc_id, context)

    if status != 200:
        return print(f"[{doc_id}, {context}] HTTP {status} error from Primo")

    if len(book) == 1:
        print(f"[{doc_id}, {context}] Encountered empty result")

        alt_context = primo.contexts[primo.contexts.index(context) - 1]
        if alt_context not in attempted_contexts:
            request_record.s(doc_id, alt_context, attempted_contexts=[*attempted_contexts, context]).apply_async()

            print(f"[{doc_id}, {context}] Attempting alt context")
        else:
            """ Prevent book from being resynced """
            store_record({
                "_id": doc_id,
                "valid": False,
                "more": {
                    "reason": "Unable to locate book",
                    "contexts": attempted_contexts,
                    "response": book
                }

            })
        return None
    print(f"[{doc_id}, {context}] Inserted Book")
    book = transform(book)
    return store_record(book)


@app.task()
def sync_views():
    utils = MongoBase.get_util_collection()

    last_query = utils.find_one("last_analytics_sync")
    minutes_ago = None
    if last_query:
        minutes_ago = ceil((datetime.now() - last_query["time"]).total_seconds() / 60)
        utils.update_one({"_id": "last_analytics_sync"}, {
            "$set": {"time": datetime.now()}
        })
    else:
        utils.insert_one({
            "_id": "last_analytics_sync",
            "time": datetime.now()
        })
    rows = generate_view_rows(minutes_ago)
    views = list(PageView(*row).mongo_representation for row in rows)

    collection = MongoBase.get_view_collection()
    collection.insert_many(views)
    print(f"{len(rows)} documents added to database")


@app.task()
def sync_books():
    """
    Locate all views which have no matching book record
    :return:
    """
    views = MongoBase.get_view_collection()
    pipeline = [
        {
            "$lookup": {
                "from": "books",
                "localField": "doc_id",
                "foreignField": "_id",
                "as": "matched_docs"
            }
        },
        {
            "$match": {"matched_docs": {"$eq": []}}
        }
    ]
    count = 0
    for view in views.aggregate(pipeline):
        request_record.s(view["doc_id"], view["context"]).apply_async()
        count += 1
    print(f"{count} record syncs added to view")


@app.task
def test(arg):
    print(arg)
