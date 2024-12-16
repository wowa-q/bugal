"""Repository Interface

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
"""
import abc


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

