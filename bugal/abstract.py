"""Abstraction layer
"""
import abc


class Command(abc.ABC):
    ''' abstract class to alighn different commands '''
    __metaclass__ = abc.ABCMeta

    # to run standard commands
    @abc.abstractmethod
    def execute(self) -> None:
        ''' interface API '''
        raise NotImplementedError


class Artifact(abc.ABC):
    """HandlerRead Interface

    APIs:
        archive
        remove_from_archive
    """
    @abc.abstractmethod
    def archive_imports(self, artifact) -> str:
        """Methode to archive the given artifact

        Raises:
            NotImplementedError:

        Returns:
            str: single transaction
        """
        raise NotImplementedError


class HandlerReadIF(abc.ABC):
    """HandlerRead Interface

    APIs:
        get_transactions
        get_meta_data
    """
    @abc.abstractmethod
    def get_transactions(self) -> str:
        """Methode to read out the transactions from an imported file

        Raises:
            NotImplementedError:

        Returns:
            str: single transaction
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_meta_data(self) -> str:
        """Methode to read out the meta data

        Raises:
            NotImplementedError:

        Returns:
            str: meta data of the import
        """
        raise NotImplementedError


class HandlerWriteIF(abc.ABC):
    """HandlerWrite Interface

    APIs:
        print() -> bool: API to print all data into the medium e.g. Excel

    """
    @abc.abstractmethod
    def print(self) -> bool:
        """Methode to execute the print

        Raises:
            NotImplementedError:

        Returns:
            bool: True if sucessful
        """
        raise NotImplementedError


class AbstractRepository(abc.ABC):
    """Interface for Repository abstraction

    Args:
        add_stack (model.Stack) -> bool: provides the stack of transactions to be stored in db 
        get_stack (model.Filter) -> model.Stack: retrieve transactions from db
        get_mapping
        set_mapping
        get_history
        set_history
        get_transaction_hashes
    Raises:
        NotImplementedError: _description_

    """
    @abc.abstractmethod
    def add_transaction(self, transaction):
        """methode to add transaction to DB

        Args:
            transaction (model.Transaction): transaction to be pushed to the DB

        Raises:
            NotImplementedError: abstract method
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_history(self, history):
        """methode to add history to DB

        Args:
            history (model.History): history to be pushed to the DB

        Raises:
            NotImplementedError: abstract method
        """
        raise NotImplementedError

    @abc.abstractmethod
    def del_history(self, *arg, **args) -> bool:
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def del_transaction(self, *arg, **args) -> bool:
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction_ctr(self) -> int:
        """_summary_

        Raises:
            NotImplementedError: _description_

        Returns:
            int: transaction counter
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_history_ctr(self) -> int:
        """_summary_

        Raises:
            NotImplementedError: _description_

        Returns:
            int: history counter
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction(self, *arg, **args):
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_history(self, *arg, **args):
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


class TransactionRepo(abc.ABC):
    __instance__ = None

    @staticmethod
    @abc.abstractmethod
    def get_instance():
        """
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, transaction) -> bool:
        """push transaction to db

        Args:
            transaction (model.Transaction): transaction instance

        Raises:
            NotImplementedError: _description_

        Returns:
            bool: True, if no error is raised
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        """get transaction from repo
        Args:
            args
                hash (str): hashstring to be searched in \
                transaction table. OR
                id_ (int): ID within the transactions table of the transaction
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, *args, **kwargs):
        """delete transaction from repo
        Args:
            args
                hash (str): hashstring to be searched in \
                transaction table. OR
                id_ (int): ID within the transactions table of the transaction
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_ctr(self) -> int:
        """retrive the counter of transaction lines

        Raises:
            NotImplementedError: _description_

        Returns:
            int: counter value
        """
        raise NotImplementedError


class HistoryRepo(abc.ABC):

    @abc.abstractmethod
    def add(self, history) -> bool:
        """push history to db

        Args:
            history (model.History): history instance

        Raises:
            NotImplementedError: _description_

        Returns:
            bool: True, if no error is raised
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        """get history from repo
        Args:
            args
                hash (str): hashstring to be searched in \
                history table. OR
                id_ (int): ID within the transactions table of the history
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, *args, **kwargs):
        """delete history from repo
        Args:
            args
                hash (str): hashstring to be searched in \
                history table. OR
                id_ (int): ID within the transactions table of the history
        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_ctr(self) -> int:
        """retrive the counter of history lines

        Raises:
            NotImplementedError: _description_

        Returns:
            int: counter value
        """
        raise NotImplementedError


class UI(abc.ABCMeta):

    @abc.abstractmethod
    def execute(self, **parameters) -> bool:
        pass
