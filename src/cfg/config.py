"""Global Bugal configuration
"""
import os
import sys
import enum
import pathlib
from datetime import datetime
import logging
import tomli


from libs import exceptions as err

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
        self.config_path = pathlib.Path("config.toml")        

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

    def load_config(self):
        """loading configuration from config.tmol
        """
        # config_file = self.get_config_path()
        config_file = self.config_path
        print(f'*** Config File: {config_file}')
        # read the config from config.toml
        with open(config_file, "rb") as toml_file:
            if toml_file is None:
                raise err.NoValidInputFilesFound(f"Config file not found {toml_file}")
            toml_config = tomli.load(toml_file)
        logger.info("Configuration loaded %s", toml_config)
        return toml_config
    

#       *** PUBLIC APIs ***
CSV_META = {
    'file_name': '',
    'file_ext': '',
    'checksum': '',
    'account': '',
    'start_date': datetime.strptime('01.01.3000', "%d.%m.%Y"),
    'end_date': datetime.strptime('01.01.1000', "%d.%m.%Y"),
}

META_TRANSACTION = {
    'tdate': '',
    'text': '',
    'status': '',
    'debitor': '',
    'verwendung': '',
    'konto': '',
    'value': '',
    'debitor_id': '',
    'mandats_ref': '',
    'customer_ref': '',
    'src_konto': '',
}
from types import SimpleNamespace


def get_config():
    cfg_ = SimpleNamespace(import_type='',
                           import_path='',
                           dbpath='',
                           archive='',
                           export_path='',
                           dbtype='')
    cfghandler = CFGToml()
    # TOML config loaded
    config = cfghandler.load_config()
    run_config = config['bugal']['run']
    print(f'*** Run Configuration: {run_config}')
    for cfg in run_config:        
        TEST = cfg.get('TEST')
        logger.info("Configuration loaded in TEST mode")
        break
    
    # configuration of files
    if 'True' in TEST:
        src_config = config['bugal']['test']
    else:
        src_config = config['bugal']['src']

    for cfg in src_config:
        # TODO: check the commented code if needed and delte if not
        SRCPATH = pathlib.Path(cfg.get('srcpath'))        
        CSVFILE = pathlib.Path(cfg.get('csv_file'))        
        DBFILE = pathlib.Path(cfg.get('db_file'))
        DBTYPE = cfg.get('repo_type')      
        ARCHIVE = pathlib.Path(cfg.get('zip_file'))        
        EXCEL = pathlib.Path(cfg.get('xls_file'))
    
    TYPE = ''
    type_config = config['bugal']['type']
    for cfg in type_config:
        #TODO: type is not needed
        TYPE = cfg.get('type')
        if cfg.get('type') == 'BETA':
            TYPECLASS = TransactionListBeta
        else:
            TYPECLASS = TransactionListClassic
    cfg_.import_type = TYPE
    cfg_.import_path = CSVFILE
    cfg_.dbpath = DBFILE
    cfg_.dbtype = DBTYPE
    cfg_.archive = ARCHIVE
    cfg_.export_path = EXCEL   
    
    return cfg_
