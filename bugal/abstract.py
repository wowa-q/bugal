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
    def create_new_db(self, pth: str, name: str, db_type: str) -> bool:
        """API to create new db

        Args:
            pth (str): path where db shall be stored
            name (str): name of the db
            db_type (str): which db type to be created e.g. sqlite

        Raises:
            NotImplementedError:

        Returns:
            bool: returns True if created
        """
        # raise NotImplementedError
        return True

    @abc.abstractmethod
    def add_stack(self, stack) -> bool:
        """API to add the stack to repository

        Args:
            stack (model.Stack): The stack from the model to be imported

        Raises:
            NotImplementedError:

        Returns:
            bool: returns True if the import was sucessful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_stack(self, fil):
        """API to get the stack out from DB by used Filter

        Args:
            fil (model.Filter): _description_

        Raises:
            NotImplementedError:

        Returns:
            model.Stack: The stack as read out from the DB
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_mapping(self):
        pass

    @abc.abstractmethod
    def set_mapping(self, mapping):
        pass

    @abc.abstractmethod
    def get_history(self):
        pass

    @abc.abstractmethod
    def set_history(self, history):
        pass

    @abc.abstractmethod
    def find_csv_checksum(self, checksum):
        """Methode to find the checksum in the DB, History table

        Args:
            checksum (_type_): _description_
        """
        pass

    @abc.abstractmethod
    def find_transaction(self, parameter, value):
        """Methode to find the transaction with the given parameter value in the DB, 
        Transactions table

        Args:
            parameter (_type_): _description_
        """
        pass