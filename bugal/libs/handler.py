"""Handlers Lib
"""
from __future__ import annotations
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any, Optional


#       *** Handlers Chain APIs ***
class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request) -> Optional[str]:
        pass


class AbstractHandler(Handler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # monkey.set_next(squirrel).set_next(dog)
        return handler

    @abstractmethod
    def handle(self, request: Any) -> str:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class PathHandler(AbstractHandler):
    def handle(self, request: Any) -> str:
        if isinstance(request, Path):
            return self.validate_path(request)
        else:
            return super().handle(request)

    def validate_path(self, _path):
        """Function for path validation, provided by user configuration

        Args:
            _path (str): path received for validation

        Returns:
            tuple(message, Path): returns message and Path type after successful validation
        """
        message = ''
        if len(_path) > 0:
            if Path(_path).is_dir():
                message = message + ' - Path configured ok \n'
            elif Path(_path).is_file():
                str(Path(_path).suffix)
                message = message + ' - File configured ok \n'
            else:
                message = message + ' - Path is incorrect \n'
                return (message, '')
        else:
            message = message + ' - Path will use working directory \n'
        return (message, Path(_path))

#       *** PUBLIC APIs ***

def validate_path(_path):
    message = ''
    if len(_path) > 0:
        if Path(_path).is_dir():
            message = message + ' - Path configured ok \n'
        elif Path(_path).is_file():
            str(Path(_path).suffix)
            message = message + ' - File configured ok \n'
        else:
            message = message + ' - Path is incorrect \n'
            return (message, '')
    else:
        message = message + ' - Path will use working directory \n'
    return (message, Path(_path))