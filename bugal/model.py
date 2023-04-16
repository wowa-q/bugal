"""
Busynes model

"""
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Transaction:
    """Transaction 
    """
    date: date
    booking_date: date
    text: str
    debitor: str
    verwendung: str
    konto: str
    blz: str
    value: int
    debitor_id: str
    mandats_ref: str
    customer_ref: str
    checksum: str
    src_konto: str

    def __hash__(self):
        data = (self.date,
             self.text,
             self.debitor,
             self.verwendung,
             self.konto,
             self.blz,
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
        self.filter = Filter()

    def init_stack(self):
        """emptying the list of transactions on created instance
        """
        self.transactions.clear()

    def create_transaction(self, data:list) -> Transaction:
        """Returns Transaction based on provided data

        Args:
            data (list): data extracted from csv file as a list

        Returns:
            Transaction: transaction object, ready for storage in DB and checking hash
        """
        try:
            date.fromisoformat(data[0])
        except ValueError:
            data[0] = '1000-01-01'
        try:
            date.fromisoformat(data[1])
        except ValueError:
            data[1] = '1000-01-01'

        transaction = Transaction(date.fromisoformat(data[0]), 
                                date.fromisoformat(data[1]), 
                                data[2], 
                                data[3], 
                                data[4], 
                                data[5], 
                                data[6], 
                                data[7], 
                                data[8], 
                                data[9], 
                                data[10], 
                                data[11], 
                                data[12])

        self.transactions.append(transaction)

        return transaction

    def push_transactions(self):
        """Push transactions to DB
        """
        seen = set()
        uniq = []
        for trns in self.transactions:
            if trns not in seen:
                uniq.append(trns)
                seen.add(trns)

        self.transactions = uniq
        self.filter.max_date = self._get_max_transaction_date()
        self.filter.min_date = self._get_min_transaction_date()

    def _get_max_transaction_date(self) -> date:
        max_date = date.fromisoformat('1000-01-01')        
        for transaction in self.transactions:
            if transaction.date > max_date:
                max_date = transaction.date
        return max_date

    def _get_min_transaction_date(self) -> date:
        min_date = date.fromisoformat('9999-01-01')
        for transaction in self.transactions:
            if transaction.date < min_date:
                min_date = transaction.date
        return min_date
    