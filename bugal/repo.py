"""_summary_

"""
import sqlite3 as sql

from . import model
from . import abstract as a


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
        # TODO SQL data request
        sql_data = None
        stack_from_db = model.Stack()
        stack_from_db.filter = fil
        
        for sql_datum in sql_data:
            stack_from_db.create_transaction(sql_datum)
        
        return stack_from_db


class SqlAlchemyRepository(a.AbstractRepository):
    """Alchemy abstraction

    Args:
        AbstractRepository (_type_): _description_
    """
    def __init__(self, session):
        self.session = session

    def add_stack(self, stack: model.Stack) -> bool:
        stack_from_db = self.get_stack(stack.filter)
        # remove douplicate entries
        for ind, new in enumerate(stack.transactions):
            for from_db in stack_from_db:
                if from_db == new:
                    stack.transactions.pop(ind)

        stack.push_transactions() 

        self.session.add(stack.transactions)

    def get_stack(self, fil: model.Filter) -> model.Stack:
        # TODO SQL data request
        sql_data = None
        stack_from_db = model.Stack()
        stack_from_db.filter = fil
        
        for sql_datum in sql_data:
            stack_from_db.create_transaction(sql_datum)
        
        return stack_from_db
    
    def get_history(self, fil:model.Filter) -> model.Stack:
        pass

    def get_mapping(self, fil:model.Filter) -> model.Stack:
        pass

    def set_history(self, his) -> bool:
        pass

    def set_mapping(self, map) -> model.Stack:
        pass
    # def get(self, reference):
    #     return self.session.query(model.Batch).filter_by(reference=reference).one()

    # def list(self):
    #     return self.session.query(model.Batch).all()

class SqlRepo():

    def __init__(self, db_type) -> None:
        self.db_type = db_type
        self.extension = '.db'

    def create_new_db(self, pth: str, name: str) -> bool:
        file_name = name + self.extension
        db_file = pth / file_name
        connection = sql.connect(db_file)

        self.cur = connection.cursor()

        return True