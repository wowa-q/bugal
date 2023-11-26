"""_summary_

"""
import types
import sqlite3 as sql
import logging

from bugal import cfg
from bugal import model
from bugal import abstract as a
# from bugal import bugal_orm


logger = logging.getLogger(__name__)


class FakeRepo(a.AbstractRepository):
    """Fake Repo for testing purpose

    Args:
        AbstractRepository (_type_): _description_
    """
    def add_stack(self, stack: model.Stack) -> bool:
        stack_from_db = self.get_stack(stack.filter)

        for ind, new in enumerate(stack.transactions):
            for from_db in stack_from_db:
                if from_db == new:
                    stack.transactions.pop(ind)

        stack.push_transactions()

    def get_stack(self, fil: model.Filter) -> model.Stack:

        sql_data = None
        stack_from_db = model.Stack(cfg.TransactionListClassic)
        stack_from_db.filter = fil

        for sql_datum in sql_data:
            stack_from_db.create_transaction(sql_datum)
        return stack_from_db

    def get_mapping(self):
        mapping = []
        return mapping

    def set_mapping(self, mapping):
        self.mapping = mapping

    def get_history(self):
        history = []
        return history

    def set_history(self, history):
        self.history = history

    def find_csv_checksum(self, checksum):
        transaction = []
        return transaction

    def find_transaction(self, parameter, value):
        transaction = []
        return transaction


class TransactionsRepo():

    def __init__(self, orm):
        if orm is None:
            raise cfg.DbConnectionFaild
        self.orm = orm

    def find_checksum(self, checksum: str):
        """Looks for the checksum of the transaction

        Args:
            checksum (str): checksum of the transaction

        Returns:
            Bool: If checksum could be found True is returned
        """
        if len(checksum) == 0:
            logger.warning("Invalid hash value received for searching: %s", checksum)
            raise cfg.RepoUseageError
        if self.orm.find_transaction_checksum(checksum) is not None :
            self.orm.close_connection()
            return True

    # def push_transactions(self, trans):
    #     """Push transactions into DB

    #     Args:
    #         trans (list): List of model.Transaction items

    #     Raises:
    #         cfg.NoValidTransactionData: if not a list is received
    #         cfg.NoValidTransactionData: if list items are not model.Transaction
    #     """
    #     if not isinstance(trans, list) or isinstance(trans, types.GeneratorType):
    #         raise cfg.NoValidTransactionData
    #     for tran in trans:
    #         if not isinstance(tran, model.Transaction):
    #             raise cfg.NoValidTransactionData
    #         self.orm.write_to_transactions(tran)
    #     self.orm.close_connection()

# class SqlAlchemyRepository(a.AbstractRepository):
#     """Alchemy abstraction

#     Args:
#         AbstractRepository (_type_): _description_
#     """
#     def __init__(self, session):
#         self.session = session

#     def add_stack(self, stack: model.Stack) -> bool:
#         stack_from_db = self.get_stack(stack.filter)
#         # remove douplicate entries
#         for ind, new in enumerate(stack.transactions):
#             for from_db in stack_from_db:
#                 if from_db == new:
#                     stack.transactions.pop(ind)

#         stack.push_transactions() 

#         self.session.add(stack.transactions)

#     def get_stack(self, fil: model.Filter) -> model.Stack:

#         sql_data = None
#         stack_from_db = model.Stack()
#         stack_from_db.filter = fil

#         for sql_datum in sql_data:
#             stack_from_db.create_transaction(sql_datum)

#         return stack_from_db

#     def get_history(self) -> model.Stack:
#         orm = bugal_orm.BugalOrm()
#         orm.read_history()
#         orm.close_connection()

#     def get_mapping(self) -> model.Stack:
#         orm = bugal_orm.BugalOrm()
#         orm.read_history()
#         orm.close_connection()

    # def set_history(self, his) -> bool:
    #     pass

    # def set_mapping(self, map) -> model.Stack:
    #     pass

    # def get(self, reference):
    #     return self.session.query(model.Batch).filter_by(reference=reference).one()

    # def list(self):
    #     return self.session.query(model.Batch).all()


class SqlRepo():

    def __init__(self, db_type) -> None:
        self.db_type = db_type
        self.extension = '.db'
        self.cur = None

    def create_new_db(self, pth: str, name: str) -> bool:
        file_name = name + self.extension
        db_file = pth / file_name
        connection = sql.connect(db_file)

        self.cur = connection.cursor()

        return True
