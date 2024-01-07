"""Definition of DB Tables
https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#classical-mappings
"""
import logging
from sqlalchemy import Column, Integer, String, Date, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


from bugal import model
from bugal import abstract as a
from bugal import cfg


logger = logging.getLogger(__name__)

Base = declarative_base()


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


# class Property(Base):
#     """Property table
#     """
#     __tablename__ = 'eigenschaften'
#     id = Column(Integer, primary_key=True)
#     inout = Column(String)
#     name = Column(String)
#     type = Column(String)
#     cycle = Column(String)
#     number = Column(Integer)
#     sum = Column(Integer)


# class Mapping(Base):
#     """Mapping table
#     """
#     __tablename__ = 'mapping'
#     id = Column(Integer, primary_key=True)
#     transaction_id = Column(Integer)
#     property_id = Column(Integer)
#     type = Column(String)
#     number = Column(Integer)
#     value = Column(Integer)


class Orm():
    """DB APIs
    """
    __instance__ = None
    __path__ = ""
    __type__ = None

    def __init__(self):
        self.engine = None
        self.session = None
        if Orm.__path__ == '':
            Orm.__path__ = cfg.DBFILE
        if Orm.__type__ is None:
            Orm.__type__ = 'sqlite'

        if Orm.__type__ == 'sqlite':
            self.engine = create_engine(f'sqlite:///{Orm.__path__}?create_db=true')
        elif Orm.__type__ == 'memory':
            self.engine = create_engine("sqlite://")
        else:
            logger.exception("Orm initialization failed, db type selection wrong %s", Orm.__type__)
            raise cfg.DbConnectionFaild(f"db type configuration failed '{Orm.__type__}'.")

        if self.engine is None:
            logger.exception("Orm: DB engine connection failed, db type selection %s", Orm.__type__)
            raise cfg.DbConnectionFaild
        Base.metadata.create_all(self.engine)
        logger.info("Repohandler was initalized with DB: %s", Orm.__path__)

    @staticmethod
    def get_instance():
        """provides instance of the SqlHistoryRepo

        Returns:
            Orm: singleton instance
        """
        if Orm.__instance__ is None:
            Orm.__instance__ = Orm()
        return Orm.__instance__

    def get_session(self):
        """provide session

        Returns:
            Session: SqlAlchemy Session
        """
        self.session = Session(self.engine)
        return self.session

    def delete_tables(self):
        """delete ALL tables from DB
        """
        tables = Base.metadata.sorted_tables
        # Löschen aller Daten aus den Tabellen
        with self.engine.connect() as conn:
            for table in tables:
                conn.execute(table.delete())

    def __enter__(self):
        return self.engine

    def __exit__(self, exc_type, exc_value, trace):
        if self.engine is not None:
            logger.info("Closing DB connection")
            self.engine.dispose()


class SqlTransactionRepo(a.TransactionRepo):
    """Implementation of sqlite Transaction Repo

    Args:
        a (TransactionRepo): Implements TransactionRepo interface
    """
    __instance__ = None
    __path__ = ""
    __type__ = None

    def __init__(self):  # tested
        """Initialization of Sql Transaction repo - Fully tested

        Args:
            pth (str, optional): Path to DB. Defaults to 'cfg.DBFILE'.
        """
        if SqlTransactionRepo.__path__ == '':
            SqlTransactionRepo.__path__ = cfg.DBFILE
            Orm.__path__ = cfg.DBFILE
        if SqlTransactionRepo.__type__ is None:
            SqlTransactionRepo.__type__ = 'sqlite'
            Orm.__type__ = 'sqlite'

        self.orm = Orm.get_instance()
        self.session = self.orm.get_session()
        self.engine = self.orm.engine

    @staticmethod
    def get_instance():  # tested
        """provides instance of the SqlHistoryRepo

        Returns:
            SqlHistoryRepo: singleton instance
        """
        if SqlTransactionRepo.__instance__ is None:
            SqlTransactionRepo.__instance__ = SqlTransactionRepo()
        return SqlTransactionRepo.__instance__

    def add(self, transaction) -> bool:  # tested
        """Initialization of Sql Transaction repo - Not fully tested
            - transaction instance - tested
            - good case writing - tested
            - duplicate raising error - tested
        Args:
            transaction (model.Transaction): transaction to be added to DB
        """
        if not isinstance(transaction, model.Transaction):
            logger.exception("""Transaction provided to push to DB is not
                             model.Transaction instance. Transaction %s""",
                             transaction)
            raise cfg.NoValidTransactionData

        duplicated = self.get(hash_=hash(transaction))
        if duplicated is not None:
            logger.exception("""Transaction provided to push to DB is duplicated. Transaction %s""",
                             transaction)
            raise cfg.ImportDuplicateTransaction

        logger.debug("""Pushing transaction to DB""")
        # umpacken ist notwendig weil checksum nicht als Attribut in diesm Dataset existiert
        t_table = Transactions(text=transaction.text,
                               datum=transaction.date,
                               status=transaction.status,
                               debitor=transaction.debitor,
                               verwendung=transaction.verwendung,
                               konto=transaction.konto,
                               value=transaction.value,
                               debitor_id=transaction.debitor_id,
                               mandats_ref=transaction.mandats_ref,
                               customer_ref=transaction.customer_ref,
                               src_konto=transaction.src_konto,
                               checksum=hash(transaction))

        with Session(self.engine) as session:
            session.add(t_table)
            session.commit()
            logger.debug("""Pushing transaction to DB completed""")
            return True

    def get(self, *args, **kwargs):  # tested
        if 'id_' in kwargs:
            with Session(self.engine) as session:
                result = session.query(Transactions).filter(Transactions.id ==
                                                            kwargs.get('id_')).first()

        elif 'hash_' in kwargs:
            with Session(self.engine) as session:
                result = session.query(Transactions).filter(Transactions.checksum ==
                                                            kwargs.get('hash_')).first()
        else:
            return None
        logger.debug("""Transaction found in DB: %s""", result)
        return result

    def remove(self, *args, **kwargs):  # tested
        with Session(self.engine) as session:
            if 'id_' in kwargs:  # tested in history
                object_to_delete = session.query(Transactions).filter_by(id=kwargs['id_']).first()
            elif 'hash_' in kwargs:  # tested
                object_to_delete = session.query(Transactions).filter_by(
                    checksum=kwargs['hash_']).first()
            else:
                return False

            if object_to_delete:
                session.delete(object_to_delete)
                session.commit()
                logger.debug("""Transaction deleted: %s""", object_to_delete)
                return True

    def get_ctr(self) -> int:  # tested
        """return the number of rows in transaction table

        Returns:
            int: number of transactions
        """
        try:
            row_count = self.session.query(func.count(Transactions.id)).scalar()
            return row_count
        except cfg.DbConnectionFaild:
            logger.exception("BugalOrm: DB session connection failed")
            return -1


class SqlHistoryRepo(a.HistoryRepo):
    """Implementation of sqlite History Repo

    Args:
        a (TransactionRepo): Implements TransactionRepo interface
    """
    __instance__ = None
    __path__ = ""
    __type__ = None

    def __init__(self):  # tested
        """Initialization of Sql History repo - Fully tested

        Args:
            pth (str, optional): Path to DB. Defaults to 'cfg.DBFILE'.
        """
        if SqlHistoryRepo.__path__ == '':
            SqlHistoryRepo.__path__ = cfg.DBFILE
            Orm.__path__ = cfg.DBFILE
        if SqlHistoryRepo.__type__ is None:
            SqlHistoryRepo.__type__ = 'sqlite'
            Orm.__type__ = 'sqlite'

        self.orm = Orm.get_instance()
        self.session = self.orm.get_session()
        self.engine = self.orm.engine

    @staticmethod
    def get_instance():  # tested
        """provides instance of the SqlHistoryRepo

        Returns:
            SqlHistoryRepo: singleton instance
        """
        if SqlHistoryRepo.__instance__ is None:
            SqlHistoryRepo.__instance__ = SqlHistoryRepo()
        return SqlHistoryRepo.__instance__

    def add(self, history) -> bool:  # tested
        """Initialization of Sql History repo - Not fully tested
            - History instance
                - good case writing - tested
                - duplicate raising error - tested
                - invalid data raising error - tested
        Args:
            History (model.History): History to be added to DB
        """
        if not isinstance(history, model.History):
            logger.exception("""History provided to push to DB is not
                             model.History instance. History %s""",
                             history)
            raise cfg.NoValidHistoryData

        duplicated = self.get(hash_=history.checksum)
        if duplicated is not None:

            logger.exception("""history provided to push to DB is duplicated. History %s""",
                             history)
            logger.info("Closing DB connection")
            raise cfg.ImportFileDuplicate

        logger.debug("""Pushing history to DB""")
        # umpacken ist notwendig weil checksum nicht als Attribut in diesm Dataset existiert
        h_table = History(file_name=history.file_name,
                          file_type=history.file_type,
                          account=history.account,
                          min_date=history.min_date,
                          max_date=history.max_date,
                          import_date=history.import_date,
                          checksum=history.checksum,)

        with Session(self.engine) as session:
            session.add(h_table)
            session.commit()
            logger.debug("""Pushing history to DB completed""")
            return True

    def get(self, *args, **kwargs):  # tested
        if 'id_' in kwargs:  # tested
            with Session(self.engine) as session:
                result = session.query(History).filter(History.id ==
                                                       kwargs.get('id_')).first()

        elif 'hash_' in kwargs:  # tested
            with Session(self.engine) as session:
                result = session.query(History).filter(History.checksum ==
                                                       kwargs.get('hash_')).first()
        else:  # tested
            return None
        logger.debug("""history found in DB: %s""", result)
        return result

    def remove(self, *args, **kwargs):  # tested
        with Session(self.engine) as session:
            if 'id_' in kwargs:  # tested
                object_to_delete = session.query(History).filter_by(id=kwargs['id_']).first()
            elif 'hash_' in kwargs:  # tested in transactions
                object_to_delete = session.query(History).filter_by(
                    checksum=kwargs['hash_']).first()
            else:
                return False

            if object_to_delete:
                session.delete(object_to_delete)
                session.commit()
                logger.debug("""history deleted: %s""", object_to_delete)
                return True

    def get_ctr(self) -> int:  # tested
        """return the number of rows in History table

        Returns:
            int: number of History
        """
        try:
            row_count = self.session.query(func.count(History.id)).scalar()
            return row_count
        except cfg.DbConnectionFaild:
            logger.exception("ORM: DB session connection failed")
            return -1
