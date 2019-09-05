import inspect
from typing import Callable

from utils.ConfigMap import ConfigMap


def receives_config(*required_keys, as_json=False):
    def receive_function(fn: Callable):
        signature = inspect.signature(fn)
        config = ConfigMap.get_singleton()
        if as_json:
            config = config.dict

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