import inspect
import os
from typing import Callable

import yaml


def get_config():
    path = os.getenv("NEBULA_CONFIG", "./config.yaml")
    with open(path, "r") as config_f:
        return yaml.load(config_f)


def receives_config(*required_keys):
    def receive_function(fn: Callable):
        signature = inspect.signature(fn)
        config = get_config()

        def wrapper(*args, **kwargs):
            if not required_keys:
                return fn(*args, config, **kwargs)
            else:
                config_args = list(config[key] if key in config else None for key in required_keys)
                return fn(*args, *config_args, **kwargs)

        wrapper.__name__ = fn.__name__
        wrapper.__signature__ = signature
        return wrapper

    return receive_function
