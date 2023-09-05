"""
Busynes model

"""
from dataclasses import dataclass, field
import dataclasses
from datetime import date, datetime

from . import cfg


@dataclass(frozen=True, eq=True)
class History:
    """Import history
    """
    file_name: str
    file_type: str
    account: str
    import_date: str
    max_date: str
    min_date: str
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
    """Transaction
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

    Returns:
        _type_: _description_
    """
    max_date: date
    min_date: date


class Stack():
    """Stack of transactions
    """

    def __init__(self):
        self.transactions = []
        self.checksums = set()
        self.filter = Filter()
        self.nr_transactions = 0
        self.header = None
        self.input_type = None
        self.src_account = ''

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()
        self.nr_transactions = 0
        self.input_type = None

    def create_history(self, history: dict) -> History:
        """_summary_

        Args:
            history (dict): data to be used for History creatiion

        Returns:
            History: History instance
        """
        data_list = []
        if isinstance(history, dict):
            # data_list = history.values
            data_list.append(history['file_name'])
            data_list.append(history['file_ext'])
            data_list.append(history['account'])
            data_list.append(history['end_date'])
            data_list.append(history['start_date'])
            data_list.append(history['checksum'])
            his = History(history['file_name'],
                          history['file_ext'],
                          history['account'],
                          datetime.now(),
                          history['end_date'],
                          history['start_date'],
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
