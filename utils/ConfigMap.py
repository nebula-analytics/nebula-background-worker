import os
from typing import Iterable, Dict, Any, Union

import yaml


class ConfigMap:
    __singleton__: 'ConfigMap' = None
    """
    A configuration mapper to make config access simpler
    """

    @classmethod
    def get_singleton(cls):
        if cls.__singleton__ is None:
            path = os.getenv("nebula.config.path", "./config.yaml")
            cls.__singleton__ = cls.load(path)
        return cls.__singleton__

    @classmethod
    def load(cls, path: str) -> 'ConfigMap':
        """
            Load the yaml config and create a ConfigMap
            Args:
                path (str) : path to config.yaml file
            Returns:
                A config map object
        """
        with open(path, "r") as config_f:
            config = yaml.safe_load(config_f)
        return ConfigMap(config)

    def __init__(self, values: Dict[str, Any], key: str = "nebula", parents: Iterable = ()):
        """
            Set up the mapper
            Args:
                values: The dictionary for this config_map
                key: The key (used to pull overrides from os.environ)
                parents: The parents of this map used to create the path
        """
        self.__values__ = values
        self.__name__ = key
        self.__parents__ = [*parents, key]
        self.__path__ = ".".join(self.__parents__)

    def __dir__(self) -> Iterable[str]:
        """
        Provide attribute hints to IDEs / Compilers
        ie: config["primo"]
        """
        return [*self.__values__.keys(), *super().__dir__()]

    def __getitem__(self, item: str):
        """
            Access this class like a dictionary
            Args:
                item (str): The key to look up
            Returns:
                ConfigMap object ie: config.primo

        """
        return self.get(item)

    def __getattr__(self, item: str):
        """
            Access this class like a object
            Args:
                item (str): The key to look up
            Returns:
                ConfigMap object ie: config.primo

        """
        return self.get(item)

    def __contains__(self, item) -> bool:
        """
            Allow dictionary style contains checks
            ie: "primo" in config
            Args:
                item (str): The key to look up
            Returns:
                True if contains. Otherwise, False.
        """

        return self.get(item) is not None

    def __iter__(self) -> Iterable[str]:
        """
            Allow iteration over raw_config values
            ie: for key in config:
            Notes:
                This method will not support additional environment keys
            Args:
                item (str): The key to look up
            Returns:

        """
        return iter(self.__values__)

    def get(self, item, default=None, json_response=False) -> Union['ConfigMap', int, float, str, list]:
        """
            Get a config variable from the configuration file or environment
            Args:
                item (str): The key to look up
                default: The value to return if no such key exists in the environment or config file
                json_response: If true, this will return a json-compatible response
            Returns:
                A config dictionary or value

        """
        environ_key = f"{self.__path__}.{item}"
        if environ_key in os.environ:
            value = os.getenv(environ_key)
            if item in self.__values__ and isinstance(self.__values__[item], dict):
                value = yaml.safe_load(value)
        else:
            value = self.__values__.get(item, default)
        if isinstance(value, dict):
            value = ConfigMap(value, key=item, parents=self.__parents__)
            if json_response:
                value = value.dict
        return value

    @property
    def dict(self):
        """
            Convert this object to a dictionary
            Notes:
                This method will not support additional environment keys
            Returns:
                A config dictionary
        """
        return {key: self.get(key, json_response=True) for key in self.__values__}

    def __repr__(self):
        return f"Config(key=\'{self.__name__}\', children=\'{', '.join(self.__values__.keys())}\')"
