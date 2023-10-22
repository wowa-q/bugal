"""_summary_
"""
import pathlib
import logging  # DEBUG, INFO, WARNING, ERROR, CRITICAL
from datetime import datetime, date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import create_engine, inspect, select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from bugal import model
from bugal import cfg

logging.basicConfig(filename='orm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()


class BugalOrm():
    """DB APIs
    """
    def __init__(self, pth, db_type='sqlite'):
        if db_type == 'sqlite':
            self.engine = create_engine(f'sqlite:///{pth}?create_db=true')
        elif db_type == 'memory':
            self.engine = create_engine("sqlite://")
        else:
            raise cfg.DbConnectionFaild(f"db type configuration failed '{db_type}'.")
        if self.engine is None:
            raise cfg.DbConnectionFaild

        self.inspector = inspect(self.engine)
        Base.metadata.create_all(self.engine)
        logging.info("Repohandler was initalized with DB: %s", pth)

    def get_transaction_ctr(self) -> int:
        """return the number of rows in transaction table

        Returns:
            int: number of transactions
        """
        try:
            with Session(self.engine) as session:
                row_count = session.query(func.count(Transactions.id)).scalar()
                return row_count
        except cfg.DbConnectionFaild:
            return -1

    def get_history_ctr(self) -> int:
        """return the number of rows in transaction table

        Returns:
            int: number of transactions
        """
        try:
            with Session(self.engine) as session:
                row_count = session.query(func.count(History.id)).scalar()
                return row_count
        except cfg.DbConnectionFaild:
            return -1

    def write_to_transactions(self, transact: model.Transaction):
        """Write new transaction to database

        Args:
            transact (model.Transaction): _description_
        """
        if not isinstance(transact, model.Transaction):
            raise ValueError
        # umpacken ist notwendig weil checksum nicht als Attribut in diesm Dataset existiert
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
        """can import a list of transactions

        Args:
            transactions (list): list of model.Transaction items

        Raises:
            cfg.ImporteFileDuplicate: if duplicate transaction is in the list
        """
        checksums = []
        for tran in transactions:
            if hash(tran) not in checksums:
                checksums.append(hash(tran))
            # skip this transaction as duplicate
            else:
                logging.info("Repohandler skipped transaction as duplicate: %s", tran)
                continue
            result = self.write_to_transactions(tran)
            if not result:
                raise cfg.ImporteFileDuplicate

    def write_to_history(self, his: model.History):
        """writing history data into repository

        Args:
            history (model.History): History row for a csv file to be imported
        """
        if not isinstance(his, model.History):
            raise ValueError
        if not isinstance(his.min_date, date):
            print('History: date not provided as datetime.date')
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
        """Pulls transactions from the DB table with the matching filter condition

        Args:
            _filter (dict): _description_

        Returns:
            list: List, which contains the rows of the table
        """
        # TODO passenden Filter basteln
        # values = []
        with Session(self.engine, future=True) as session:
            if 'date-after' in _filter:
                results = session.query(Transactions).filter(Transactions.datum > _filter['date-after']).all()

                # query = select(Transactions).where(Transactions.datum.like(_filter['date-after']))
                # results = session.query(Transactions).filter(Transactions.datum.in_(values)).all()
                # query = select(Transactions).where(Transactions.datum.like('2022-01%'))
                # result = session.execute(query).scalars().all()
            else:
                return None

            return results

    def read_history(self, ) -> list:
        """read the history rows from the DB table

        Returns:
            list: History entraces (rows)
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
    datum = Column(Date)
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
    min_date = Column(Date)
    max_date = Column(Date)
    import_date = Column(Date)
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
