"""
Busynes model

"""
from dataclasses import dataclass, field
import dataclasses
from datetime import date

from . import cfg
# from . import cli
# from . import repo


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
    date: date = field(metadata='printed')
    text: str = field(metadata='printed')  # changed
    status: str
    debitor: str    # renamed
    verwendung: str = field(metadata='printed')  # moved 1x to left
    konto: str = field(metadata='printed')  # changed
    value: int = field(metadata='printed')  # renamed
    debitor_id: str
    mandats_ref: str
    customer_ref: str
    # checksum: str = field(metadata='printed')
    src_konto: str = field(metadata='printed')

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

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()
        self.nr_transactions = 0
        self.input_type = None

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

        try:
            date.fromisoformat(data[col.DATE.value])
        except ValueError:
            data[col.DATE.value] = '1000-01-01'

        # Text or status is existing
        try:
            status = data[col.STATUS.value]
            text = '-'
        except AttributeError:
            status = '-'
            text = data[col.TEXT.value]
        # TODO: fill konto with real data
        try:
            konto = data[col.KONTO.value]
        except AttributeError:
            konto = '-'

        transaction = Transaction(date.fromisoformat(data[col.DATE.value]),
                                  text,
                                  status,
                                  data[col.RECEIVER.value],
                                  data[col.VERWENDUNG.value],
                                  konto,
                                  data[col.VALUE.value],
                                  data[col.DEBITOR_ID.value],
                                  data[col.MANDATS_REF.value],
                                  data[col.CUSTOMER_REF.value],
                                  data[11])

        if hash(transaction) not in self.checksums:
            self.transactions.append(transaction)
            self.checksums.add(hash(transaction))
        self.nr_transactions = len(self.transactions)

        return transaction

    def push_transactions(self):
        """Push transactions to DB
        """
        self.filter.max_date = self._get_max_transaction_date()
        self.filter.min_date = self._get_min_transaction_date()

    def update_history(self, hist: list):
        """push import history into database
        """
        history = History(hist[0],
                          hist[1],
                          hist[2],
                          date.fromisoformat(hist[3]),
                          date.fromisoformat(hist[4]),
                          date.fromisoformat(hist[5]),
                          hist[6])
        print(history)

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
