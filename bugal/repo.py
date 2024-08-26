"""_summary_

"""
import logging
from datetime import datetime

from bugal import model
from bugal import abstract as a
from bugal import repo_adapter
from bugal import exceptions as err
# from bugal import bugal_orm


logger = logging.getLogger(__name__)


class FakeRepo(a.AbstractRepository):
    """Fake Repo for testing purpose

    Args:
        AbstractRepository (_type_): _description_
    """
    def __init__(self, tctr=0, hctr=0):
        self.tctr = tctr    # transaction counter
        self.hctr = hctr    # history counter
        self.hashes = []
        self.hists = []
        self.trns = []

    def add_transaction(self, transaction: model.Transaction):  # tested
        if isinstance(transaction, model.Transaction):
            crc = hash(transaction)
            if crc in self.hashes:
                raise err.ImportDuplicateTransaction('Fake: dobule transaction')
            else:
                self.hashes.append(crc)
                self.trns.append(transaction)
                self.tctr += 1
            return True
        else:
            raise err.NoValidTransactionData('Fake: transaction not type of Transaction')

    def add_history(self, history: model.History):
        if isinstance(history, model.History):
            crc = history.checksum
            if crc in self.hashes:
                raise err.ImportFileDuplicate('Fake: csv already imported')
            else:
                self.hashes.append(crc)
                self.hists.append(history)
                self.hctr += 1
            return True
        else:
            raise err.NoValidHistoryData('Fake: history not type of History')

    def get_transaction_ctr(self) -> int:
        return self.tctr

    def get_history_ctr(self) -> int:
        return self.hctr

    def get_transaction(self, *arg, **args) -> model.Transaction:
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        if len(self.trns) > 0:
            return self.trns[0]

    def get_history(self, *arg, **args) -> model.History:
        """_summary_

        Raises:
            NotImplementedError: _description_
        """
        if len(self.hists) > 0:
            return self.hists[0]

    def del_history(self, *arg, **args) -> bool:
        """emulates deleting history from table
        """
        self.hashes = []
        self.hctr -= 1
        return True

    def del_transaction(self, *arg, **args) -> bool:
        """emulates deleting history from table
        """
        self.hashes = []
        self.tctr -= 1
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"


class TransactionsRepo(a.AbstractRepository):
    """Repository resource for transactions
    """
    def __init__(self, pth='', db_type='sqlite'):  # tested
        self.adapter = repo_adapter.RepoAdapter(pth, db_type)

    def deinit(self):
        """to close the connection
        """
        self.adapter.deinit()

    def add_transaction(self, transaction: model.Transaction):  # tested
        result = False
        result = self.adapter.add_transaction(transaction)
        logger.debug("""Pushing transaction to DB""")
        return result

    def get_transaction_ctr(self) -> int:  # tested
        ctr = self.adapter.get_transaction_ctr()
        return ctr

    def get_transaction(self, *arg, **kwargs) -> model.Transaction:  # tested
        """retrive transaction from DB by ID or hash value

        Returns:
            orm.Transaction: transaction row from table
        """
        if 'id_' in kwargs:  #
            return self.adapter.get_transaction(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  #
            return self.adapter.get_transaction(hash_=kwargs.get('hash_'))
        elif 'start_date' in kwargs:  # start_date - end_date
            if not isinstance(kwargs.get('start_date'), datetime):
                print(f'Transaction filter ist nicht datetime.datetime: {kwargs}')
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            print(f'lese Bereich von {start_date} bis {end_date}')
            return self.adapter.get_transaction(start_date=start_date,
                                                end_date=end_date)
        else:
            print(f'kein passender Argument gefunden: {kwargs}')
            return None

    def del_transaction(self, *arg, **kwargs) -> bool:  # tested
        """deleting transaction from table"""
        logger.debug("""Deleting transaction from DB: %s""", kwargs)
        if 'id_' in kwargs:  #
            return self.adapter.del_transaction(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  #
            return self.adapter.del_transaction(hash_=kwargs.get('hash_'))
        else:
            return False

    # interface satisfaction
    def del_history(self, *arg, **kwargs) -> bool:
        raise NotImplementedError

    def add_history(self, history):
        raise NotImplementedError

    def get_history_ctr(self):
        raise NotImplementedError

    def get_history(self, *arg, **kwargs):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} using {self.adapter}"


class HistoryRepo(a.AbstractRepository):
    """Repository resource for history
    """
    def __init__(self, pth='', db_type='sqlite'):  # tested
        self.adapter = repo_adapter.RepoAdapter(pth=pth, db_type=db_type)

    def add_history(self, history: model.History):  # tested
        result = False
        result = self.adapter.add_history(history)
        logger.debug("""Pushing history to DB""")
        return result

    def get_history(self, *arg, **kwargs) -> model.History:  # tested
        if 'id_' in kwargs:  # tested
            return self.adapter.get_history(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.adapter.get_history(hash_=kwargs.get('hash_'))
        else:
            return None

    def get_history_ctr(self) -> int:  # tested
        ctr = self.adapter.get_history_ctr()
        return ctr

    def del_history(self, *arg, **kwargs) -> bool:  # tested
        """deleting history from table
        """
        logger.debug("""Deleting history from DB: %s""", kwargs)
        if 'id_' in kwargs:  # tested
            return self.adapter.del_history(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.adapter.del_history(hash_=kwargs.get('hash_'))
        else:
            return False

    # interface satisfaction
    def add_transaction(self, transaction):
        raise NotImplementedError

    def get_transaction_ctr(self):
        raise NotImplementedError

    def get_transaction(self, *arg, **kwargs):
        raise NotImplementedError

    def del_transaction(self, *arg, **kwargs) -> bool:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} using {self.adapter}"
