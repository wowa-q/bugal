"""Global Bugal configuration
"""
import os
import sys
import enum
import pathlib
from datetime import datetime
import logging
import tomli

from bugal import exceptions as err

logging.basicConfig(filename='bugal.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

MIN_COL = 2
MAX_COL = 100
MIN_ROW = 5
MAX_ROW = 100


def get_config_path():
    # Falls die Anwendung von PyInstaller ausgeführt wird
    if getattr(sys, 'frozen', False):
        # Path zum Verzeichnis, in dem die ausführbare Datei liegt
        app_dir = pathlib.Path(sys._MEIPASS)
    else:
        # Falls das Skript normal ausgeführt wird
        os.chdir(pathlib.Path(__file__).parent.resolve())
        app_dir = pathlib.Path(__file__).parent.resolve()

    # Pfad zur Konfigurationsdatei relativ zum Anwendungsverzeichnis
    config_path = app_dir / "config.toml"

    return config_path


# Ändere das Arbeitsverzeichnis zum Verzeichnis des Ausführungsskripts
os.chdir(pathlib.Path(__file__).parent.resolve())
PTOJECT_DIR = pathlib.Path(__file__).parent.resolve()
ARCHIVE = PTOJECT_DIR.resolve() / 'BUGAL.zip'
BUGALSPACE = PTOJECT_DIR.parent.resolve() / 'bugal_p'
DB_NAME = "bugal_default.db"
FIXTURE_DIR = PTOJECT_DIR.parent.resolve() / 'tests/fixtures'

CSVFILE = None
DBFILE = None
ARCHIVE = None
EXCEL = None
TEST = True


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


def load_config():
    """loading configuration from config.tmol
    """
    config_file = get_config_path()
    # read the config from config.toml
    with open(config_file, "rb") as toml_file:
        if toml_file is None:
            raise err.NoValidInputFilesFound(f"Config file not found {toml_file}")
        toml_config = tomli.load(toml_file)
    logger.info("Configuration loaded %s", toml_config)

    return toml_config


config = load_config()
run_config = config['bugal']['run']
for cfg in run_config:
    TEST = bool(cfg.get('TEST'))
    logger.info("Configuration loaded in TEST mode")
    break

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
    if cfg.get('type') == 'BETA':
        TYPECLASS = TransactionListBeta
    else:
        TYPECLASS = TransactionListClassic

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


