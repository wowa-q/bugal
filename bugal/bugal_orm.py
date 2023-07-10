"""_summary_
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import model
from . import cfg

Base = declarative_base()


class BugalOrm():
    """DB APIs
    """
    def __init__(self, pth, name, db_type='sqlite'):
        if db_type == 'sqlite':
            filename = name + '.db'
            db_file = pth / filename
        else:
            db_file = cfg.PTOJECT_DIR / 'new_temp.db'

        self.engine = create_engine(f'sqlite:///{db_file}')

        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def write_to_transactions(self, transact: model.Transaction):
        """Write new transaction to database

        Args:
            transact (model.Transaction): _description_
        """
        transaction = Transactions(text=transact.text,
                                   datum=transact.date,
                                   status=transact.status,
                                   debitor=transact.debitor,
                                   verwendung=transact.verwendung,
                                   konto=transact.konto,
                                   value=transact.value,
                                   debitor_id=transact.debitor_id,
                                   mandats_ref=transact.mandats_ref,
                                   customer_ref=transact.customer_ref,
                                   src_konto=transact.src_konto,
                                   checksum=transact.text)

        self.session.add(transaction)
        self.session.commit()

    def write_many_to_transactions(self, transactions: list):
        """Write new transaction to database

        Args:
            transact (model.Transaction): _description_
        """
        t_list = []
        for tran in transactions:
            transaction = Transactions(text=tran.text,
                                       datum=tran.date,
                                       status=tran.status,
                                       debitor=tran.debitor,
                                       verwendung=tran.verwendung,
                                       konto=tran.konto,
                                       value=tran.value,
                                       debitor_id=tran.debitor_id,
                                       mandats_ref=tran.mandats_ref,
                                       customer_ref=tran.customer_ref,
                                       src_konto=tran.src_konto,
                                       checksum=tran.text)
            t_list.append(transaction)
        self.session.add_all(t_list)
        self.session.commit()
    
    def write_to_history(self, history: model.History):
        history = History(file_name=history.file_name,
                          file_type=history.file_type,
                          account=history.account,
                          min_date=history.min_date,
                          max_date=history.max_date,
                          import_date=history.import_date,
                          checksum=history.checksum)
        
        self.session.add(history)
        self.session.commit()

    def write_to_history(self, property: model.Property):
        property = Property(inout=property.inout,
                          name=property.name,
                          type=property.type,
                          cycle=property.cycle,
                          # number=1,               # muss beim Update/setzen incrementiert werden
                          # sum=property.sum,
                          )
        
        self.session.add(property)
        self.session.commit()


################################################################
#                        Tables                                #
################################################################


class Transactions(Base):
    """Transaction table
    """
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    datum = Column(String)
    text = Column(String)
    status = Column(String)
    debitor = Column(String)
    verwendung = Column(String)
    konto = Column(String)
    value = Column(Integer)
    debitor_id = Column(String)
    mandats_ref = Column(String)
    customer_ref = Column(String)
    src_konto = Column(String)
    checksum = Column(String)


class History(Base):
    """History table
    """
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    file_type = Column(String)
    account = Column(String)
    min_date = Column(String)
    max_date = Column(String)
    import_date = Column(String)
    checksum = Column(String)


class Property(Base):
    """Property table
    """
    __tablename__ = 'property'
    id = Column(Integer, primary_key=True)
    inout = Column(String)
    name = Column(String)
    type = Column(String)
    cycle = Column(String)
    number = Column(Integer)
    sum = Column(Integer)


class Mapping(Base):
    """Mapping table
    """
    __tablename__ = 'mapping'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer)
    property_id = Column(Integer)
    type = Column(String)
    number = Column(Integer)
    value = Column(Integer)


# class Rules(Base):
#     """rules table
#     """
#     __tablename__ = 'rules'
#     id = Column(Integer, primary_key=True)
#     pattern = Column(String)
#     inout = Column(String)
#     property_id = Column(Integer)
#     cycle = Column(String)
#     number = Column(String)
#     sum = Column(String)
