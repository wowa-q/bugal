
import logging

from . import orm
from . import db_if as a

logger = logging.getLogger(__name__)


class RepoAdapter(a.AbstractRepository):
    """Repo Adapter selects the right repository driver
    supported:
        - sqlite
        - sqlite (memory)
    """
    def __init__(self, config):  
        self.config = config
        self.db_type = self.config.dbtype
        self.pth = self.config.dbpath
        self.trepo = None
        self.hrepo = None
        if self.db_type in ['sqlite', 'memory']:
            orm.SqlTransactionRepo.__path__ = self.pth
            orm.SqlTransactionRepo.__type__ = self.db_type
            orm.SqlHistoryRepo.__path__ = self.pth
            orm.SqlHistoryRepo.__type__ = self.db_type
            logger.debug("""ADAPTER initialization: path: %s and type: %s""",
                         orm.SqlTransactionRepo.__path__,
                         orm.SqlTransactionRepo.__type__)
        else:
            logger.debug("""No adapter found for transaction to DB: %s""", self.db_type)

    def set_config(self, config):
        self.config = config

    def deinit(self):
        """closing connection to DB
        """
        if self.trepo is not None:
            self.trepo.deinit()

    def add_transaction(self, transaction):  # tested
        result = False

        logger.debug("""Pushing transaction to DB: sqlite""")
        if self.trepo is None:
            self.trepo = orm.SqlTransactionRepo.get_instance(self.config)
        result = self.trepo.add(transaction)
        return result

    def add_history(self, history):  # tested
        result = False

        logger.debug("""Pushing history to DB: sqlite""")
        if self.hrepo is None:
            self.hrepo = orm.SqlHistoryRepo.get_instance(self.config)
        result = self.hrepo.add(history)
        return result

    def get_transaction(self, *args, **kwargs):  # tested
        if self.trepo is None:
            self.trepo = orm.SqlTransactionRepo.get_instance(self.config)

        if 'id_' in kwargs:  # tested
            return self.trepo.get(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.trepo.get(hash_=kwargs.get('hash_'))
        elif 'start_date' in kwargs:  # start_date - end_date
            return self.trepo.get(start_date=kwargs.get('start_date'),
                                  end_date=kwargs.get('end_date'))
        else:
            return None

    def get_history(self, *args, **kwargs):
        if self.hrepo is None:
            self.hrepo = orm.SqlHistoryRepo.get_instance(self.config)

        if 'id_' in kwargs:  # tested
            return self.hrepo.get(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.hrepo.get(hash_=kwargs.get('hash_'))

        else:
            return None

    def get_transaction_ctr(self):  # tested
        result = -1

        if self.trepo is None:
            self.trepo = orm.SqlTransactionRepo.get_instance(self.config)
        result = self.trepo.get_ctr()
        return result

    def get_history_ctr(self):  # tested
        result = -1

        if self.hrepo is None:
            self.hrepo = orm.SqlHistoryRepo.get_instance(self.config)
        result = self.hrepo.get_ctr()
        return result

    def del_history(self, *arg, **kwargs) -> bool:  # tested
        """ deleting history from table
        """
        if self.hrepo is None:
            self.hrepo = orm.SqlHistoryRepo.get_instance(self.config)
        logger.debug("""Deleting history from DB: %s""", kwargs)
        if 'id_' in kwargs:  # tested
            return self.hrepo.remove(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.hrepo.remove(hash_=kwargs.get('hash_'))
        else:
            return False

    def del_transaction(self, *arg, **kwargs) -> bool:  # tested
        """ deleting transaction from table
        """
        if self.hrepo is None:
            self.hrepo = orm.SqlTransactionRepo.get_instance(self.config)
        logger.debug("""Deleting transaction from DB: %s""", kwargs)
        if 'id_' in kwargs:  # tested
            return self.hrepo.remove(id_=kwargs.get('id_'))
        elif 'hash_' in kwargs:  # tested
            return self.hrepo.remove(hash_=kwargs.get('hash_'))
        else:
            return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for {self.db_type} located in {self.pth}"
