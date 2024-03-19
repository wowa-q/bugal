"""
Busynes model

"""

from dataclasses import dataclass, field
import dataclasses
from datetime import date, datetime
import logging

from bugal import exceptions as err
# from bugal import repo

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
        # self.trepo = repo.TransactionsRepo()
        logger.info("Stack initialized with input type: %s", input_type)

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()
        self.nr_transactions = 0
        self.input_type = None
        self.checksums.clear()
        self.src_account = ''
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
        if isinstance(datum, datetime):
            logger.debug("datum provided not as string, but as datetime: %s", datum)
            return datum
        newdate = None

        if len(datum) == 8:
            newdate = datetime.strptime(datum, '%d.%m.%y').date()
        elif len(datum) == 10:
            newdate = datetime.strptime(datum, '%d.%m.%Y').date()
        else:
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

    def create_history(self, history: dict) -> History:
        """The API is creating a History Dataclass instance,
            which can be used to be imported into DB.
            history needs to have:
            - 'end_date': str object representing a date in a format '%d.%m.%Y'
            - 'start_date': str object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums
              from History table in DB
            - ?
        Args:
            history (dict): data to be used for History creatiion
        Raises:
            err.NoValidHistoryData: if data provided not as dict
        Returns:
            History: History instance
        """
        if isinstance(history, dict):
            end_date = self._make_date(history.get('end_date'))
            start_date = self._make_date(history.get('start_date'))

            his = History(history['file_name'],
                          history['file_ext'],
                          history['account'],
                          datetime.now(),
                          end_date,             # history['end_date'],
                          start_date,           # history['start_date'],
                          history['checksum'])
            self.set_src_account(history['account'])
        else:
            logger.debug("History is not instance of dict")
            raise err.NoValidHistoryData(f"datum provided with false format: {history}")

        return his

    def set_src_account(self, account: str):
        """is required to be initialized with the account which is imported.
        needs to be retrieved from the csv meta data

        Args:
            account (str): account from which to report
        """
        logger.info("source account set to: %s", account)
        self.src_account = account

    def create_transaction(self, data: list) -> Transaction:
        """Returns Transaction based on provided data

        Args:
            data (list): data extracted from csv file as a list

        Raises:
            bugal.exceptions.NoInputTypeSet: input_type needs to be set before using the Stack
            bugal.exceptions.NoValidTransactionData: validation of provided transaction data failed
            AttributeError: raised when DATE does't exist in input_type
        Returns:
            Transaction: transaction object, ready for storage in DB and checking hash
        """
        if self.input_type is None:     # cfg.TransactionListBeta or cfg.TransactionListClassic
            logger.debug("NoInputTypeSet is not set")
            raise err.NoInputTypeSet('Model: input type not configured')
        if not isinstance(data, list):
            logger.debug("#Data provided is not instance of list")
            raise err.NoValidTransactionData('Model: Transaction data not as list')
        # check that only real data are provided
        if len(data) < 7:
            logger.debug("#Data provided has not correct length: %s", len(data))
            raise err.NoValidTransactionData(f'Model: Transaction data list to short: {len(data)}')
        # calculate date
        date_obj = None
        atrs = dir(self.input_type)
        if 'DATE' in atrs:
            date_string = data[self.input_type.DATE.value]
            date_obj = self._make_date(date_string)
        else:
            logger.debug("Transaction date invalid for transaction: %s", data)
            raise AttributeError
        if 'STATUS' in atrs:
            status = data[self.input_type.STATUS.value]
            text = '-'
        else:
            status = '-'
            text = data[self.input_type.TEXT.value]
        if 'KONTO' in atrs:
            konto = data[self.input_type.KONTO.value]
        else:
            # new fashion csv doesn't provide account
            konto = '-'

        if self.src_account is not None:
            src_konto = self.src_account
        else:
            logger.debug("Source account not initialized: %s", self.src_account)
            raise err.NoValidTransactionData('Model: Source account not set')

        value = self._make_num(str(data[self.input_type.VALUE.value]))
        transaction = Transaction(date_obj,
                                  text,
                                  status,
                                  data[self.input_type.RECEIVER.value],
                                  data[self.input_type.VERWENDUNG.value],
                                  konto,
                                  value,
                                  data[self.input_type.DEBITOR_ID.value],
                                  data[self.input_type.MANDATS_REF.value],
                                  data[self.input_type.CUSTOMER_REF.value],
                                  src_konto)

        if hash(transaction) not in self.checksums:
            self.transactions.append(transaction)
            self.checksums.add(hash(transaction))

        self.nr_transactions = len(self.transactions)

        return transaction

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

    # PLANNED METHODS
    def push_transactions(self, transaction):
        """Push transactions to DB
        """
        # TODO: not implermented
        self.filter.max_date = self._get_max_transaction_date()
        self.filter.min_date = self._get_min_transaction_date()
        # self.trepo.add_transaction(transaction)
        raise NotImplementedError

    def update_history(self, hist: list):
        """push import history into database
        """
        # TODO: not implermented
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
