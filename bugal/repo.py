"""_summary_

"""
import abc

from . import model

class AbstractRepository(abc.ABC):
    """Interface for Repository abstraction

    Args:
        add_stack (model.Stack) -> bool: provides the stack of transactions to be stored in db 
        get_stack (model.Filter) -> model.Stack: retrieve transactions from db
        get_mapping
        set_mapping
        get_history
        set_history
    Raises:
        NotImplementedError: _description_

    """
    @abc.abstractmethod  
    def add_stack(self, stack: model.Stack) -> bool:
        raise NotImplementedError  

    @abc.abstractmethod
    def get_stack(self, fil: model.Filter) -> model.Stack:
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

class FakeRepo(AbstractRepository):
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

class SqlAlchemyRepository(AbstractRepository):
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
    
    # def get(self, reference):
    #     return self.session.query(model.Batch).filter_by(reference=reference).one()

    # def list(self):
    #     return self.session.query(model.Batch).all()