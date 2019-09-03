from Primo import *
from Primo.transform import transform

app = Celery('tasks', broker='amqp://localhost')


@app.task()
def import_record(doc_id: str, context: str):
    if book_exists(doc_id):
        return
    book = get_book(doc_id, context)
    book = transform(book)
    store_record(book)
    return True

