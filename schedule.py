from typing import Tuple, Optional

from Analytics.PageView import PageView
from Primo import *
from Primo.transform import transform
from main import view_selection_help
from utils import receives_config

app = Celery()

receives_config("celery", as_json=True)(app.config_from_object)()


@app.task()
def import_record(doc_id: str, context: str) -> Tuple[Optional[str], str]:
    """
    Import a primo book record into the database
    :param doc_id: The primo doc_id
    :param context: The primo context, L or PC
    :return: The database id or None and a debug string result
    """
    if book_exists(doc_id):
        return None, "Already exists"
    book = get_book(doc_id, context)
    book = transform(book)
    return store_record(book), "Inserted"


@app.task()
def sync_views():
    view_selection_help()


@app.task()
def insert_view(row: list):
    view = PageView(*row)
    view.store()
    book = view.get_book()
    if book is None:
        import_record.s(view.doc_id, view.context).apply_async()


@app.task
def test(arg):
    print(arg)
