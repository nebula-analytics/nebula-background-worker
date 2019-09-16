from datetime import datetime, timedelta
from math import floor
from typing import Optional, Union

from celery import Celery

from Analytics.PageView import PageView
from Analytics.helpers import generate_view_rows
from Primo import *
from Primo.transform import transform
from utils import receives_config

app = Celery("schedule")

receives_config("celery", as_json=True)(app.config_from_object)()


# MongoBase.get_book_collection().create_index([("doc_id", pymongo.TEXT)], unique=True)


@app.task
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
    update_record(doc_id, status="processing")

    book, status = get_book(doc_id, context)

    if status != 200:
        update_record(doc_id, status="failed", status_values={"message": f"HTTP {status}", "body": book})
        raise RuntimeError("Non-Ok status returned by primo")

    if len(book) == 1:
        alt_context = primo.contexts[primo.contexts.index(context) - 1]
        if alt_context not in attempted_contexts:
            request_record.s(doc_id, alt_context, attempted_contexts=[*attempted_contexts, context]).apply_async()
            return f"[{doc_id}, {context}] Attempting alt context"
        else:
            """ Prevent book from being resynced """
            update_record(**{
                "_id": doc_id,
                "status": "failed",
                "status_values": {
                    "reason": "Unable to locate book",
                    "contexts": attempted_contexts,
                    "response": book
                }

            })
        return f"[{doc_id}, {context}] Book not located"
    print(f"[{doc_id}, {context}] Inserted Book")
    book = transform(book)
    return update_record(**book, status="processed", status_values={})


@app.task()
def sync_views():
    utils = MongoBase.get_util_collection()

    last_query = utils.find_one("last_analytics_sync")
    minutes_ago = None
    if last_query:
        minutes_ago = floor((datetime.now() - last_query["time"]).total_seconds() / 60)
        utils.update_one({"_id": "last_analytics_sync"}, {
            "$set": {"time": datetime.now()}
        })
    else:
        utils.insert_one({
            "_id": "last_analytics_sync",
            "time": datetime.now()
        })
    rows = generate_view_rows(minutes_ago)
    views = list(PageView(*row) for row in rows)
    views = list(view for view in views if not view.exists())

    print(f"[Sync Views] {len(views)} new views received from analytics")
    if views:
        collection = MongoBase.get_view_collection()
        return repr(collection.insert_many(list(v.mongo_representation for v in views)))


@app.task()
def sync_books():
    """
    Locate all views which have no matching book record
    :return:
    """
    views = MongoBase.get_view_collection()
    books = MongoBase.get_book_collection()
    collections = ConfigMap.get_singleton().database.mongodb.collections

    pipeline = [
        {
            "$group": {"_id": "$doc_id", "context": {"$first": "$context"}}
        }, {
            "$lookup": {
                "from": collections.books,
                "localField": "_id",
                "foreignField": "doc_id",
                "as": "matched_docs"
            }
        },
        {
            "$match": {
                "$or": [
                    {"matched_docs": {"$eq": []}},
                    {"$and": [
                        {"matched_docs.task.retry_at": {"$lte": datetime.now()}},
                        {"matched_docs.status": {"$not": {"$in": ["failed", "processed"]}}}
                    ]}
                ]}
        }
    ]

    queue = list(
        {
            "doc_id": view["_id"],
            "status": "queued",
            "status_values": {
                "record": view,
            },
            "task": {
                "task_id": request_record.s(view["_id"], view["context"]).apply_async().id,
                "retry_at": datetime.now() + timedelta(days=1),
            }
        }
        for view in views.aggregate(pipeline)
    )
    print(f"[Sync Books] {len(queue)} books in diff")
    if queue:
        books.insert_many(queue)


@app.task
def test(arg):
    print(arg)
