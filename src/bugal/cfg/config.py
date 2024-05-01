"""Global Bugal configuration
"""
import os
import sys
import enum
import pathlib
from datetime import datetime
import logging
import tomli

from bugal.libs import exceptions as err

logging.basicConfig(filename='bugal.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ändere das Arbeitsverzeichnis zum Verzeichnis des Ausführungsskripts
os.chdir(pathlib.Path(__file__).parent.resolve())
PTOJECT_DIR = pathlib.Path(__file__).parent.resolve()
BUGALSPACE = PTOJECT_DIR.parent.resolve() / 'bugal_p'
FIXTURE_DIR = PTOJECT_DIR.parent.resolve() / 'tests/fixtures'

MIN_COL = 2
MAX_COL = 100
MIN_ROW = 5
MAX_ROW = 100

CSVFILE = None
DBFILE = None
ARCHIVE = None
EXCEL = None
TEST = True

# setting default values
ARCHIVE = PTOJECT_DIR.resolve() / 'BUGAL.zip'
DB_NAME = "bugal_default.db"


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


class CFG():
    """Global configuration
    """
    MIN_COL = 2
    MAX_COL = 100
    MIN_ROW = 5
    MAX_ROW = 100

    CSVFILE = None
    DBFILE = None
    ARCHIVE = None
    EXCEL = None
    TYPECLASS = None
    TYPE = ''
    TEST = True

    # setting default values
    ARCHIVE = PTOJECT_DIR.resolve() / 'BUGAL.zip'
    DB_NAME = "bugal_default.db"

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


class CFGToml(CFG):
    """TOML configuration
    """
    def __init__(self):
        pass

    def get_config_path(self):
        """getting path for toml configuration

        Returns:
            pathlib.Path: Path to the TOML file
        """
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


#       *** PUBLIC APIs ***
from types import SimpleNamespace


def get_config():
    cfg_ = SimpleNamespace(path_='', import_type='')
    
    return cfg_
