"""
Busynes model

"""

from dataclasses import dataclass, field
import dataclasses
from datetime import date, datetime
import logging
from pathlib import Path

from libs import exceptions as err
from bugal.db import repo
# import the handlers
from bugal.app import csv_handler
from bugal.app import bugal_if as a
# from bugal.app import xls_handler
from bugal.app import gen_handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True, eq=True)
class History:
    """Datclass of History, for importing into DB
    """
    file_name: str
    file_type: str
    account: str
    import_date: date
    max_date: date
    min_date: date
    checksum: str

    def __iter__(self):
        for feld in dataclasses.fields(self):
            yield getattr(self, feld.name)


@dataclass(frozen=True, eq=True)
class Property:
    """
    Property
    """
    inout: str
    name: str
    type: str
    cycle: str

    def __iter__(self):
        for feld in dataclasses.fields(self):
            yield getattr(self, feld.name)


@dataclass(frozen=True, eq=True)
class Transaction:
    """Transaction is a Dataclass fot creation of the transactions
    """
    date: date = field(metadata={'printed': True})
    text: str = field(metadata={'printed': True})  # changed
    status: str
    debitor: str    # renamed
    verwendung: str = field(metadata={'printed': True})  # moved 1x to left
    konto: str = field(metadata={'printed': True})  # changed
    value: int = field(metadata={'printed': True})  # renamed
    debitor_id: str
    mandats_ref: str
    customer_ref: str
    src_konto: str = field(metadata={'printed': True})

    def __iter__(self):
        for feld in dataclasses.fields(self):
            yield getattr(self, feld.name)
    #TODO: Reduce! Es kommt zu unterschiedlichen Checksumen!
    def __hash__(self):
        data = (self.date,
                self.text,
                self.status,
                self.debitor,
                self.verwendung,
                self.konto,
                self.value,
                self.src_konto,
                self.mandats_ref,
                self.customer_ref
                )
        return hash(data)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Filter():
    """Filter template for DB

    """
    max_date: date
    min_date: date


class Stack():
    """Stack of transactions
    """

    def __init__(self, input_type):
        self.transactions = []
        self.checksums = set()
        self.filter = Filter()
        self.nr_transactions = 0
        self.input_type = input_type
        self.src_account = ''
        self.repo_type = 'sqlite'
        self.trepo = None
        self.hrepo = None
        self.import_meta:dict = None
        self.history = None         #TODO: wenn meta schon gibt, braucht es doch keine History?
        self.import_adapter = None
        logger.info("Stack initialized with input type: %s", input_type)

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()
        self.nr_transactions = 0
        self.input_type = None
        self.checksums.clear()
        self.src_account = ''
        self.trepo = None
        self.hrepo = None
        self.import_meta = None
        self.history = None
        self.import_adapter = None
        logger.info("Stack re-initialized with input type: %s", self.input_type)

    def _make_date(self, datum: str) -> date:
        """Create date from String

        Args:
            datum (str): Datum extracted from Csv file

        Raises:
            err.InvalidTimeFormat: if unknown format was provided

        Returns:
            date: Date
        """
        if datum is None:
            raise err.InvalidTimeFormat("datum provided with false format: None")
        
        if isinstance(datum, datetime):
            logger.debug("datum provided not as string, but as datetime: %s", datum)
            return datum
        newdate = None
        try:
            newdate = datetime.strptime(datum, '%d.%m.%y').date()
        except ValueError:
            try:
                newdate = datetime.strptime(datum, '%d.%m.%Y').date()
            except ValueError:
                logger.exception("datum provided with false format: %s", datum)
                raise err.InvalidTimeFormat(f"datum provided with false format: {datum}")
            
        return newdate

    def _make_num(self, value: str) -> float:
        """Providing value as float number for calculation

        Args:
            value (str): Extracted value from Csv file

        Returns:
            float: converted value
        """
        cleaned_string = value
        if '€' in value:
            cleaned_string = value[:-2]
        cleaned_string = cleaned_string.replace(' €', '')
        cleaned_string = cleaned_string.replace('.', '')  # erst die tausender weg
        cleaned_string = cleaned_string.replace(',', '.')
        cleaned_string = ''.join(char for char in cleaned_string if char.isdigit() or char == '-' or char == '.')
        logger.debug("cleaned string: %s", cleaned_string)
        return float(cleaned_string)

    # das Datum wird aus csv history extrahiert. Braucht man das noch?
    def _get_max_transaction_date(self) -> date:
        max_date = date.fromisoformat('1000-01-01')
        for transaction in self.transactions:
            if transaction.date > max_date:
                max_date = transaction.date
        logger.info("Maximum transaction date found: %s", max_date)
        return max_date

    # das Datum wird aus csv history extrahiert. Braucht man das noch?
    def _get_min_transaction_date(self) -> date:
        min_date = date.fromisoformat('9999-01-01')
        for transaction in self.transactions:
            if transaction.date < min_date:
                min_date = transaction.date
        logger.info("Minimum transaction date found: %s", min_date)
        return min_date
    
    def create_history(self, meta: dict) -> History:
        """The API is creating a History Dataclass instance,
            which can be used to be imported into DB.
            meta needs to have:
            - 'end_date': str object representing a date in a format '%d.%m.%Y'
            - 'start_date': str object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums
              from History table in DB
            - ?
        Args:
            meta (dict): data to be used for History creatiion:
                - 'end_date': datetime object in format '%d.%m.%Y'
                - 'start_date': datetime object in format '%d.%m.%Y'
                - 'account': string object showing from which account the data were exported
                - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
                - 'file_name': (str) showing the file name
                - 'file_ext': showing the file extension
        Raises:
            err.NoValidHistoryData: if data provided not as dict
        Returns:
            History: History instance
        """
        if isinstance(meta, dict):
            end_date = self._make_date(meta.get('end_date'))
            start_date = self._make_date(meta.get('start_date'))

            his = History(meta['file_name'],
                          meta['file_ext'],
                          meta['account'],
                          datetime.now(),
                          end_date,             # meta['end_date'],
                          start_date,           # meta['start_date'],
                          meta['checksum'])
            self.set_src_account(meta['account'])
        else:
            logger.debug("meta is not instance of dict")
            raise err.NoValidHistoryData(f"datum provided with false format: {meta}")
        self.import_meta = his
        return his

    def set_src_account(self, account: str):
        """is required to be initialized with the account which is imported.
        needs to be retrieved from the csv meta data

        Args:
            account (str): account from which to report
        """
        logger.info("source account set to: %s", account)
        self.src_account = account

    def create_transaction(self, data: dict) -> Transaction:
        """Returns Transaction based on provided data

        Args:
            data (dict): data extracted from csv file as a dictionary

        Raises:
            
            bugal.exceptions.NoValidTransactionData: validation of provided transaction data failed
            AttributeError: raised when DATE does't exist in input_type
        Returns:
            Transaction: transaction object, ready for storage in DB and checking hash
        """
        if not isinstance(data, dict):
            logger.debug("#Data provided is not instance of dict")
            raise err.NoValidTransactionData(f'Model: Transaction data not as dict {data}')        
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            logger.debug("Source account not initialized: %s", self.src_account)
            raise err.NoValidTransactionData('Model: Source account not set')
        value = self._make_num(str(data.get('value')))
        date_obj = self._make_date(data.get('tdate'))
        transaction = Transaction(date_obj,
                                  data.get('text'),
                                  data.get('status'),
                                  data.get('debitor'),
                                  data.get('verwendung'),
                                  data.get('konto'),
                                  value,
                                  data.get('debitor_id'),
                                  data.get('mandats_ref'),
                                  data.get('customer_ref'),
                                  src_konto)

        if hash(transaction) not in self.checksums:
            self.transactions.append(transaction)
            self.checksums.add(hash(transaction))

        self.nr_transactions = len(self.transactions)

        return transaction

    # PLANNED METHODS
    def push_transactions(self, transaction):
        """Push transactions to DB
        """
        # TODO: push_transactions not implermented
        self.filter.max_date = self._get_max_transaction_date()
        self.filter.min_date = self._get_min_transaction_date()
        # self.trepo.add_transaction(transaction)
        raise NotImplementedError

    def update_history(self, hist: list):
        """push import history into database
        """
        # TODO: update_history not implermented
        # history = History(hist[0],
        #                   hist[1],
        #                   hist[2],
        #                   date.fromisoformat(hist[3]),
        #                   date.fromisoformat(hist[4]),
        #                   date.fromisoformat(hist[5]),
        #                   hist[6])
        logger.info("History was updated")
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: bugal busyness logic"


#       *** PUBLIC APIs ***
#soll der Pfad über config reingeholt werden?
def get_history_repo(pth_):
    repo.HistoryRepo(pth=pth_, db_type='sqlite')

def get_transaction_repo(pth_):
    repo.HistoryRepo(pth=pth_, db_type='sqlite')

# tested, without checking already imported branch
def validate_import_file(config) -> bool:
    """The function is validating the path of the import, 
    selecting the right adapter and stores it into Stack, 
    checking if the csv file is already existing in DB,
    geting meta data and stores it into Stack, 
    
    Args:
        config (SimpleNamed): configuration of different pathes

    Raises:
        err.NoCsvFilesFound: file for beeing imported not found

    Returns:
        (Bool): result True if successful
    """
    genh = gen_handler.PathHandler()
    (msg, csvpth) = genh.validate_path(config.import_path)
    if len(str(csvpth)) == 0:
        print(msg)
        logger.debug(msg)
        raise err.NoCsvFilesFound(f'Model: input File not found: {config.import_path}')   
    else:
        return True

def make_stack(config):
    """ 
    selecting the right adapter and stores it into Stack, 
    geting meta data and stores it into Stack, 
    
    Args:
        config (_type_): configuration of different pathes

    Raises:
        err.NoInputTypeSet: If the selector does not exist

    Returns:
        stack(Stack): instance of stack, which is configured for further process
    """
    # build the right adapter first (match exists since Python 3.10) -> workaround with dict:
    selector = {
        "CLASSIC": csv_handler.ClassicInputAdapter,
        "Modern": csv_handler.ModernInputAdapter,
        "DailyCard": csv_handler.DailyCardAdapter,
        "Modern_2024": csv_handler.ModernInput_2024Adapter,
    }
    if config.import_type not in selector:
        print(f"This input type is not supported: {config.import_type}")
        raise err.NoInputTypeSet(f"Input type is not supported: {config.import_type}")
    csv_adapter = selector.get(config.import_type)(config.import_path)
    
    # leave the function if checksum exists in DB history    
    # csv_checksum = csv_adapter.get_checksum(csvpth)
    meta = csv_adapter.get_meta_data()
    stack = Stack(config.import_type)
    stack.import_meta = meta
    stack.import_adapter = csv_adapter

    return stack

def compare_hash(csv_checksum, dbpath:Path):
    """ 
    checking if the csv file is already existing in DB    
    
    Args:
        csv_checksum (str): hash which will be searched in DB
        dbpath (pathlib.Path): DB path

    Returns:
        found(sql): sql response or None, if hash was not found
    """
    # search the checksum in the meta table
    # check if checksum already exists
    ''''''
    hrepo = repo.HistoryRepo(pth=dbpath)
    found = hrepo.get_history(hash_=csv_checksum)
    return found


def start_csv_import(config, stack):
    repo_type='sqlite'
    try:
        meta = stack.import_meta
        csv_adapter = stack.import_adapter
        # history_entry = stack.create_history(meta)
    except AttributeError:
        logger.debug("No valid stack received")
        raise err.ModelStackError
    if meta is None or csv_adapter is None:
        logger.debug("No valid stack received - no meta or import_adapter provided")
        raise err.ModelStackError
    elif not isinstance(csv_adapter, a.ICSVAdapter):
        logger.debug("No valid stack received - broken import_adapter provided")
        raise err.ModelStackError
    
    ctr_t = 0
    # get transaction row generator
    for _, transrow in enumerate(csv_adapter.get_transaction()):
        # build Transaction
        tran = stack.create_transaction(transrow)
        # check if transaction exists already in db
        trepo = repo.TransactionsRepo(pth=config.dbpath, db_type=repo_type)
        found = trepo.get_transaction(hash_=hash(tran))
        if found is not None:
            # an entry was found with the same hash -> transaction exists already
            logger.warning("CmdImportNewCsv: transaction already imported: %s", tran)
            # exit the execution
            continue
        else:
            trepo.add_transaction(tran)
            ctr_t += 1

    return ctr_t
            
def update_history(config, stack):
    hrepo = repo.HistoryRepo(pth=config.dbpath)
    history_entry = stack.create_history(stack.import_meta)
    result = hrepo.add_history(history_entry)
    return result

def archive_import_file(config):    
    archiver = gen_handler.ArtifactHandler(config.archive)
    archiver.archive_imports(config.import_path)
