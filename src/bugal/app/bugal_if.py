"""Abstraction layer
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

class Artifact(ABC):
    """HandlerRead Interface

    APIs:
        archive
        remove_from_archive
    """
    @abstractmethod
    def archive_imports(self, artifact) -> str:
        """Methode to archive the given artifact

        Raises:
            NotImplementedError:

        Returns:
            str: single transaction
        """
        raise NotImplementedError

################################################################
#               Default Handler responsibility chain                          
################################################################
class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler):
        """_summary_

        Args:
            handler (Handler): _description_

        Returns:
            Handler: _description_
        """
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

class AbstractInputHandler(ABC):
    """Input Handler abstraction

    APIs:
        get_meta_from_classic (None): -> dict provide input file meta data as dict
        get_meta_from_modern (None): -> dict provide input file meta data as dict
        get_meta_from_dcard (None): -> dict provide input file meta data as dict

    Raises:
        NotImplementedError: _description_
    """
    @abstractmethod
    def get_meta_from_classic(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_meta_from_modern(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError
        
    @abstractmethod
    def get_meta_from_dcard(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError

    @abstractmethod
    def get_transaction_from_classic(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_transaction_from_modern(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_transaction_from_dcard(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError

    @abstractmethod
    def get_history_from_classic(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_history_from_modern(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_history_from_dcard(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    
################################################################
#                Flexible Handler - Adapter logic                                
################################################################
class ICSVAdapter(ABC):
    """HandlerRead Interface

    APIs:
        get_transactions
        get_meta_data
        get_history
    """
    __instance__ = None

    @staticmethod
    @abstractmethod
    def get_instance():
        """
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_transaction(self):
        """Methode to read out the transactions from an imported file

        Raises:
            NotImplementedError:

        Returns:
            Transaction: single transaction
        """
        raise NotImplementedError

    @abstractmethod
    def get_meta_data(self) -> dict:
        """Methode to read out the meta data

        Raises:
            NotImplementedError:

        Returns:
            dict: meta data from input file
        """
        raise NotImplementedError
    
    

################################################################
#                  Excel Handler Undefined patern
################################################################
class HandlerWriteIF(ABC):
    """HandlerWrite Interface

    APIs:
        print() -> bool: API to print all data into the medium e.g. Excel

    """
    @abstractmethod
    def print(self) -> bool:
        """Methode to execute the print

        Raises:
            NotImplementedError:

        Returns:
            bool: True if sucessful
        """
        raise NotImplementedError

