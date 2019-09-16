import inspect
import os
import pickle
from pickle import UnpicklingError
from typing import Callable

# noinspection PyPackageRequirements
from google.auth.transport.requests import Request
# noinspection PyPackageRequirements
from googleapiclient.discovery import build

from utils import receives_config, ConfigMap


class AuthenticationException(Exception):
    pass


class GAuth:
    _cached_creds = None

    @classmethod
    def require(cls, service_name, version):
        """
        Args:
            service_name (str): the name of the service (analytics)
            version: (str): version of the service (v3)
        Returns:
            authentication for service
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
        """
           Args:
               service (str): the name of the service (analytics)
               version: (str): version of the service (v3)
           Returns:
               authentication for service
        """
        token = cls._get_token()
        return build(service, version, credentials=token, cache_discovery=False)

    @classmethod
    def _get_token(cls):
        """
            Args:
            Raises:
                AuthenticationException: If the token is invalid
            Returns:
                valid token
        """
        if cls._cached_creds is None:
            cls._cached_creds = cls._load_token_file()
        token = cls._cached_creds
        if cls._validate_token(token):
            return token
        raise AuthenticationException("The provided token is marked as 'invalid'")

    @classmethod
    def _validate_token(cls, token):
        """
            Args:
                token (Optional[pickle]): token file (token.pickle)
            Raises:
                AuthenticationException: If the token is expired and is not refreshable
            Returns:
                valid token
        """
        if token.expired:
            if token.refresh_token:
                token.refresh(Request())
            else:
                raise AuthenticationException("The provided token is marked as expired and is not refreshable")
        return token.valid

    @classmethod
    @receives_config("analytics")
    def _load_token_file(cls, analytics: ConfigMap):
        """
            Args:
                analytics (ConfigMap): contains viewID and path to token file
            Raises:
                AuthenticationException: If the provided token file is empty
                AuthenticationException: If the provided token file is corrupted or unable to be loaded
                AuthenticationException: If the provided token file is not a valid token pickle file.
            Returns:
                valid token
        """
        if os.path.isfile(analytics.path_to_credentials):
            try:
                with open(analytics.path_to_credentials, "rb") as tokenf:
                    token = pickle.load(tokenf)
                    if not token:
                        raise AuthenticationException(
                            f"The provided token file '{analytics.path_to_credentials}' was empty")
                    return token
            except UnpicklingError:
                raise AuthenticationException(
                    f"The provided token file '{analytics.path_to_credentials}' is corrupted and could not be loaded")
        else:
            raise AuthenticationException(
                f"The provided token file '{analytics.path_to_credentials}' was not a valid file object")
