"""Global Bugal configuration
"""
import enum
import pathlib
from datetime import datetime

import tomli

MIN_COL = 2
MAX_COL = 100
MIN_ROW = 5
MAX_ROW = 100

PTOJECT_DIR = pathlib.Path(__file__).parent.resolve()
ARCHIVE = PTOJECT_DIR.resolve() / 'BUGAL.zip'
BUGALSPACE = PTOJECT_DIR.parent.resolve() / 'bugal_p'
DB_NAME = "bugal_default.db"
FIXTURE_DIR = PTOJECT_DIR.parent.resolve() / 'tests/fixtures'


def load_config():
    """loading configuration from config.tmol
    """
    # read the config from config.toml
    with open(PTOJECT_DIR / "config.toml", "rb") as toml_file:
        toml_config = tomli.load(toml_file)
    return toml_config


config = load_config()
run_config = config['bugal']['run']
for cfg in run_config:
    TEST = bool(cfg.get('TEST'))
    break

CSVFILE = None
DBFILE = None
ARCHIVE = None
EXCEL = None


print(f'TEST: {TEST}')
# configuration of files
if TEST:
    src_config = config['bugal']['test']
else:
    src_config = config['bugal']['src']

for cfg in src_config:
    # TODO: check the commented code if needed and delte if not
    SRCPATH = pathlib.Path(cfg.get('srcpath'))
    # if pathlib.Path(cfg.get('csv_file')).is_file():
    CSVFILE = pathlib.Path(cfg.get('csv_file'))
    # if pathlib.Path(cfg.get('db_file')).is_file():
    DBFILE = pathlib.Path(cfg.get('db_file'))
    # if pathlib.Path(cfg.get('zip_file')).is_file():
    ARCHIVE = pathlib.Path(cfg.get('zip_file'))
    # if pathlib.Path(cfg.get('xls_file')).is_file():
    EXCEL = pathlib.Path(cfg.get('xls_file'))

TYPE = ''
type_config = config['bugal']['type']
for cfg in type_config:
    TYPE = cfg.get('type')

CSV_META = {
    'file_name': '',
    'file_ext': '',
    'checksum': '',
    'account': '',
    'start_date': datetime.strptime('01.01.3000', "%d.%m.%Y"),
    'end_date': datetime.strptime('01.01.1000', "%d.%m.%Y"),
}

# Excel columns
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

# class TransactionsSheetCfg(enum.Enum):
#     """Configuration Transaction table in excel
#     """
#     MIN_COL = 2
#     MAX_COL = 100
#     MIN_ROW = 5
#     MAX_ROW = 100


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


class ModelStackError(Exception):
    """ Raised if stack produce an error
    """


class ConstructorTypeErrors(TypeError):
    """
    Helper class that holds a list of error messages. Intended to capture all TypeErrors
    encountered during a
    constructor call, instead of raising only the first one.
    """

    messages: list[str]

    def __init__(self, messages: list[str]):
        self.messages = messages

    def get_messages(self):
        """Provide Exception error message

        Returns:
            list: list of messages to be reported by the exception
        """
        return list(self.messages)


class RepoUseageError(Exception):
    """Raised if Repo is not used in correct way
    """
