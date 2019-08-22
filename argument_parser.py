import argparse
import inspect
from typing import Callable


def get_args():
    parser = argparse.ArgumentParser(description='Run the background service worker to keep '
                                                 'the database in sync with real time analytics views')
    parser.add_argument("path_to_token", type=str, help="The file path to a file containing current/ up-to date"
                                               " credentials for google cloud")
    parser.add_argument("--view_id", type=str, default=None,
                        help="The google analytics view id to use in requests, if you"
                             " leave this blank the program will list available views.")
    return parser.parse_args()


def receive_arguments(fn: Callable):
    signature = inspect.signature(fn)
    argument_dict = dict(get_args()._get_kwargs())
    expected = set(signature.parameters.keys()).intersection(argument_dict.keys())

    def wrapper(*args, **kwargs):
        kwargs = {**{key: argument_dict[key] for key in expected}, **kwargs}
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    wrapper.__signature__ = signature
    return wrapper
