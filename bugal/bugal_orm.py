"""_summary_
"""
import pathlib
import logging  # DEBUG, INFO, WARNING, ERROR, CRITICAL

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import model
from . import cfg

logging.basicConfig(filename='orm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()


class BugalOrm():
    """DB APIs
    """
    def __init__(self, pth='', name='', db_type='sqlite'):
        if db_type == 'sqlite':
            if pathlib.Path(pth).is_file():
                db_file = pth
            else:
                db_file = str(pth) + '/' + name + '.db'
            self.engine = create_engine(f'sqlite:///{db_file}')
        elif db_type == 'memory':
            self.engine = create_engine("sqlite://")
        else:
            db_file = cfg.PTOJECT_DIR / 'new_temp.db'
            self.engine = create_engine(f'sqlite:///{db_file}')

        if self.engine is None:
            raise cfg.DbConnectionFaild

        self.inspector = inspect(self.engine)
        Base.metadata.create_all(self.engine)
        logging.info("Repohandler was initalized with DB: %s", pth)

    def write_to_transactions(self, transact: model.Transaction):
        """Write new transaction to database

        Args:
            transact (model.Transaction): _description_
        """
        if not isinstance(transact, model.Transaction):
            raise ValueError
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
                                   checksum=hash(transact))
        try:
            with Session(self.engine) as session:
                session.add(transaction)
                session.commit()
                return True
        except IntegrityError as exc:
            print("IntegrityError:", exc)
            print(f"""csv file with {transaction} was already imported,
                  checksum {transaction.checksum} exists""")
            return False
        except cfg.ImporteFileDuplicate:
            print(f"csv file with {transaction} was already imported")
            return False

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
                                       checksum=hash(tran))
            t_list.append(transaction)
        try:
            with Session(self.engine) as session:
                session.add_all(t_list)
                session.commit()
                return True
        except IntegrityError as exc:
            print("IntegrityError:", exc)
            print(f"""csv file with {transaction} was already imported,
                  checksum {hash(transaction)} exists""")
            return False
        except cfg.ImporteFileDuplicate:
            print(f"csv file with {transaction} was already imported")
            return False

    def write_to_history(self, his: model.History):
        """writing history data into repository

        Args:
            history (model.History): History row for a csv file to be imported
        """
        if not isinstance(his, model.History):
            raise ValueError
        history = History(file_name=his.file_name,
                          file_type=his.file_type,
                          account=his.account,
                          min_date=his.min_date,
                          max_date=his.max_date,
                          import_date=his.import_date,
                          checksum=his.checksum)

        try:
            with Session(self.engine) as session:
                session.add(history)
                session.commit()
                return True
        except IntegrityError as exc:
            print("IntegrityError:", exc)
            print(f"""csv file with {history} was already imported,
                  checksum {history.checksum} exists""")
            return False
        except cfg.ImporteFileDuplicate:
            print(f"csv file with {history} was already imported")
            return False

    def write_to_property(self, prop: model.Property):
        eigenschaften = Property(inout=prop.inout,
                                 name=prop.name,
                                 type=prop.type,
                                 cycle=prop.cycle,
                                 # number=1,               # muss beim Update/setzen incrementiert werden
                                 # sum=property.sum,
                                 )
        with Session(self.engine) as session:
            session.add(eigenschaften)
            session.commit()

    def read_transactions(self, _filter: dict) -> list:
        # TODO passenden Filter basteln
        with Session(self.engine, future=True) as session:
            query = select(Transactions).where(Transactions.datum.like('2022-01%'))
            result = session.execute(query).scalars().all()

        return result

    def read_history(self, ) -> list:
        """_summary_

        Returns:
            list: History entraces
        """
        with Session(self.engine, future=True) as session:
            query = select(History)
            result = session.execute(query).scalars().all()

        return result

    def close_connection(self):
        """closing DB connection
        """
        self.engine.dispose()

    def find_csv_checksum(self, hash_string=''):
        """find the checksum in the history table

        Args:
            hash_string (str, optional): _description_. Defaults to ''.

        Raises:
            cfg.DbConnectionFaild: _description_

        Returns:
            _type_: _description_
        """
        with Session(self.engine, future=True) as session:

            if not self.inspector.has_table('History'):
                raise cfg.DbConnectionFaild
            # Überprüfen, ob der Hash in der Tabelle "History" vorhanden ist
            result = session.query(History).filter(History.checksum == hash_string).first()
            # query = select(History).where(History.checksum.like(hash_string))
            # result = session.execute(query).scalars().all()
        # just information found or not is needed
        return result is not None
        # return query

    def find_transaction_checksum(self, hash_string=''):
        """find the checksum in the transactions table

        Args:
            hash_string (str, optional): hashstring to be searched in \
                transaction table. Defaults to ''.

        Returns:
            Bool: Found checksum or not
        """
        with Session(self.engine, future=True) as session:
            # test if such table exists
            if not self.inspector.has_table('transactions'):
                raise cfg.DbConnectionFaild
            # Überprüfen, ob der Hash in der Tabelle "Transactions"
            # vorhanden ist
            result = session.query(Transactions).filter(Transactions.checksum == hash_string).first()
        # just information found or not is needed
        return result is not None

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
    checksum = Column(String, unique=True)


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
    checksum = Column(String, unique=True)


class Property(Base):
    """Property table
    """
    __tablename__ = 'eigenschaften'
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
