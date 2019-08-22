import inspect
import os
import pickle
from pickle import UnpicklingError
from typing import Callable

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from argument_parser import receive_arguments


class AuthenticationException(Exception):
    pass


class GAuth:
    _cached_creds = None

    @classmethod
    def require(cls, service_name, version):
        """
        Annotate a method with the access required, the access object
        will be passed to the last argument
        :param service_name:
        :param version:
        :return:
        """

        def receive(fn: Callable):
            def wrapper(*args, **kwargs):
                auth = cls.build_access(service_name, version)
                args = list(args)
                args.append(auth)
                return fn(*args, **kwargs)

            wrapper.__name__ = fn.__name__
            wrapper.__signature__ = inspect.signature(fn)
            return wrapper

        return receive

    @classmethod
    def build_access(cls, service: str, version: str):
        token = cls._get_token()
        return build(service, version, credentials=token)

    @classmethod
    def _get_token(cls):
        if cls._cached_creds is None:
            cls._cached_creds = cls._load_token_file()
        token = cls._cached_creds
        if cls._validate_token(token):
            return token
        raise AuthenticationException("The provided token is marked as 'invalid'")

    @classmethod
    def _validate_token(cls, token):
        if token.expired:
            if token.refresh_token:
                token.refresh(Request())
            else:
                raise AuthenticationException("The provided token is marked as expired and is not refreshable")
        return token.valid

    @classmethod
    @receive_arguments
    def _load_token_file(cls, path_to_token: str):
        if os.path.isfile(path_to_token):
            try:
                with open(path_to_token, "rb") as tokenf:
                    token = pickle.load(tokenf)
                    if not token:
                        raise AuthenticationException(f"The provided token file '{path_to_token}' was empty")
                    return token
            except UnpicklingError:
                raise AuthenticationException(
                    f"The provided token file '{path_to_token}' is corrupted and could not be loaded")
        else:
            raise AuthenticationException(f"The provided token file '{path_to_token}' was not a valid file object")
