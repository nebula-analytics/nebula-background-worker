def start():
    while True:
        pass


def add_book(doc_id: str):
    pass


def add_view(document: dict):
    """
    1. Check document doc_id is in books
    2. If it isn't request book info from primo
    3. Add primo data to books
    :param document:
    :return:
    """
    print(document)


def update():
    """
    1. Retrieve analytics
    2. Call add_view on each view

    :return:
    """
    pass


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
