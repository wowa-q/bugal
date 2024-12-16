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


class AbstractInputHandler(abc.ABC):
    """Input Handler abstraction

    APIs:
        get_meta_from_classic (None): -> dict provide input file meta data as dict
        get_meta_from_modern (None): -> dict provide input file meta data as dict
        get_meta_from_dcard (None): -> dict provide input file meta data as dict

    Raises:
        NotImplementedError: _description_
    """
    @abc.abstractmethod
    def get_meta_from_classic(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_meta_from_modern(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError
        
    @abc.abstractmethod
    def get_meta_from_dcard(self) -> dict:
        """API to retrieve input file meta data

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            dict: meta data of the input file
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction_from_classic(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_transaction_from_modern(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_transaction_from_dcard(self):
        """API to create Transaction data class diefined by the model

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            Generator(Transaction): transaction data class, ready to be pushed into DB
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_history_from_classic(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_history_from_modern(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_history_from_dcard(self, meta: dict):
        """API to History data class for input file

        Raises:
            NotImplementedError: must be implemented by the user

        Returns:
            History: data class of the input file
        """
        raise NotImplementedError
    

class HandlerReadIF(abc.ABC):
    """HandlerRead Interface

    APIs:
        get_transactions
        get_meta_data
        get_history
    """
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
    def get_transaction(self):
        """Methode to read out the transactions from an imported file

        Raises:
            NotImplementedError:

        Returns:
            Transaction: single transaction
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_meta_data(self) -> dict:
        """Methode to read out the meta data

        Raises:
            NotImplementedError:

        Returns:
            dict: meta data from input file
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_history(self, meta: dict):
        """Methode to read out the meta data

        Raises:
            NotImplementedError:

        Returns:
            History: data for the import
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
