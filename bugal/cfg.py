"""Global Bugal configuration
"""
import enum
import pathlib
from datetime import datetime

PTOJECT_DIR = pathlib.Path(__file__).parent.resolve()

MIN_COL = 2
MAX_COL = 100
MIN_ROW = 5
MAX_ROW = 100

COLUMNS = {
    'Datum': 2,
    'Buchungstext': 3,
    'Verwendungszweck': 4,
    'Kontonummer': 5,
    'Status': 6,
    'Betrag': 7,
    'vom Konto': 8,
    'Checksum': 9,
}

CSV_META = {
    'file_name': '',
    'file_ext': '',
    'checksum': '',
    'account': '',
    'start_date': datetime.strptime('01.01.3000', "%d.%m.%Y"),
    'end_date': datetime.strptime('01.01.1000', "%d.%m.%Y"),
}


class InputType(enum.Enum):
    """Configuration which input is expected (e.g. classic csv)
    """
    CLASSIC = 0
    BETA = 1


class TransactionsSheetCfg(enum.Enum):
    """Configuration Transaction table in excel
    """
    MIN_COL = 2
    MAX_COL = 100
    MIN_ROW = 5
    MAX_ROW = 100


class TransactionListClassic(enum.Enum):
    """Position in the list from classic csv"""
    DATE = 0
    TEXT = 2
    RECEIVER = 3
    VERWENDUNG = 4
    KONTO = 5
    VALUE = 7
    DEBITOR_ID = 8
    MANDATS_REF = 9
    CUSTOMER_REF = 10
    CSV_START_ROW = 6


class TransactionListBeta(enum.Enum):
    """Position in the list from Beta (new) csv"""
    DATE = 0
    STATUS = 2
    SENDER = 3
    RECEIVER = 4
    VERWENDUNG = 5
    VALUE = 7
    DEBITOR_ID = 8
    MANDATS_REF = 9
    CUSTOMER_REF = 10
    CSV_START_ROW = 4


class NoInputTypeSet(Exception):
    """Input type is required for correct processing of the input
    """


class NoValidTransactionData(Exception):
    """ Raised if not valid transaction data were provided
    """


class NoValidInputFilesFound(Exception):
    """ Raised if not valid transaction data were provided
    """


class DbConnectionFaild(Exception):
    """ Raised if not valid transaction data were provided
    """


class ImporteFileDuplicate(Exception):
    """ Raised if not valid transaction data were provided
    """
