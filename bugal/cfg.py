"""Global Bugal configuration
"""
import enum

MIN_COL = 2
MAX_COL = 100
MIN_ROW = 5
MAX_ROW = 100

COLUMNS = {
    'Datum':2,
    'Buchungstext': 3,
    'Verwendungszweck':4,
    'Kontonummer':5,
    'BLZ':6,
    'Betrag':7,
    'vom Konto':8,
    'Checksum':9, 
}
CSV_START_ROW = 7

class TransactionsSheetCfg(enum.Enum):
    """Configuration Transaction table in excel
    """
    MIN_COL = 2
    MAX_COL = 100
    MIN_ROW = 5
    MAX_ROW = 100

class NoCsvFilesFound(Exception):
    """Exception if in given folder no CSV files could be found"""