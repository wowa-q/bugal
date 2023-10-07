"""
Busynes model

"""
from dataclasses import dataclass, field
import dataclasses
from datetime import date, datetime

# from . import cfg
from bugal import cfg


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
                self.src_konto
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

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()
        self.nr_transactions = 0
        self.input_type = None
        self.checksums.clear()
        self.src_account = ''

    def _make_date(self, datum: str) -> date:
        if isinstance(datum, datetime):
            return datum
        try:
            newdate = datetime.strptime(datum, '%d.%m.%Y').date()
        except ValueError:
            print(f'datum provided with false format: {datum}')
        return newdate

    def create_history(self, history: dict) -> History:
        """The API is creating a History Dataclass instance,
            which can be used to be imported into DB.
            history needs to have:
            - 'end_date': str object representing a date in a format '%d.%m.%Y'
            - 'start_date': str object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
            - ?
        Args:
            history (dict): data to be used for History creatiion
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
            return None

        return his

    def set_src_account(self, account: str):
        """is required to be initialized with the account which is imported.
        needs to be retrieved from the csv meta data

        Args:
            account (str): _description_
        """
        self.src_account = account

    def create_transaction(self, data: list) -> Transaction:
        """Returns Transaction based on provided data

        Args:
            data (list): data extracted from csv file as a list

        Raises:
            cfg.NoInputTypeSet: input_type needs to be set before using the Stack
            cfg.NoValidTransactionData: validation of provided transaction data failed
            cfg.NoValidTransactionData: validation of provided transaction data failed
            cfg.NoValidTransactionData: validation of provided transaction data failed

        Returns:
            Transaction: transaction object, ready for storage in DB and checking hash
        """
        if self.input_type is None:     # cfg.TransactionListBeta or cfg.TransactionListClassic
            raise cfg.NoInputTypeSet
        else:
            col = self.input_type
        if not isinstance(data, list):
            raise cfg.NoValidTransactionData
        # check that only real data are provided
        if len(data) < 7:
            raise cfg.NoValidTransactionData

        date_format = "%d.%m.%Y"  # Das Format, in dem das Datum vorliegt
        date_obj = None
        try:
            date_string = data[col.DATE.value]
            date_obj = datetime.strptime(date_string, date_format).date()
        except ValueError:
            print(f'Transaction date invalid for transaction: {data}')

        # Text or status is existing
        try:
            status = data[col.STATUS.value]
            text = '-'
        except AttributeError:
            status = '-'
            text = data[col.TEXT.value]
        try:
            konto = data[col.KONTO.value]
        except AttributeError:
            # new fashion csv doesn't provide account
            konto = '-'

        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise cfg.NoValidTransactionData

        transaction = Transaction(date_obj,
                                  text,
                                  status,
                                  data[col.RECEIVER.value],
                                  data[col.VERWENDUNG.value],
                                  konto,
                                  data[col.VALUE.value],
                                  data[col.DEBITOR_ID.value],
                                  data[col.MANDATS_REF.value],
                                  data[col.CUSTOMER_REF.value],
                                  src_konto)

        if hash(transaction) not in self.checksums:
            self.transactions.append(transaction)
            self.checksums.add(hash(transaction))
            # self.nr_transactions += 1
        self.nr_transactions = len(self.transactions)

        return transaction

    # das Datum wird aus csv history extrahiert. Braucht man das noch?
    def _get_max_transaction_date(self) -> date:
        max_date = date.fromisoformat('1000-01-01')
        for transaction in self.transactions:
            if transaction.date > max_date:
                max_date = transaction.date
        return max_date

    # das Datum wird aus csv history extrahiert. Braucht man das noch?
    def _get_min_transaction_date(self) -> date:
        min_date = date.fromisoformat('9999-01-01')
        for transaction in self.transactions:
            if transaction.date < min_date:
                min_date = transaction.date
        return min_date

    # PLANNED METHODS
    def push_transactions(self):
        """Push transactions to DB
        """
        # TODO: not implermented
        self.filter.max_date = self._get_max_transaction_date()
        self.filter.min_date = self._get_min_transaction_date()

    def update_history(self, hist: list):
        """push import history into database
        """
        # TODO: not implermented
        history = History(hist[0],
                          hist[1],
                          hist[2],
                          date.fromisoformat(hist[3]),
                          date.fromisoformat(hist[4]),
                          date.fromisoformat(hist[5]),
                          hist[6])
        print(history)
