import pathlib
import hashlib
from datetime import datetime
import logging
import csv


from bugal import cfg
from bugal import abstract as a
from bugal import exceptions as err
from bugal.model import Transaction, History


logger = logging.getLogger(__name__)

class InputMaster():
    """ Provides generic operations - must not be used outside of 
        handler implementation.
    """
    
    def get_checksum(self, csv_file: pathlib.Path):
        """provides hash value for csv file

        Args:
            csv_file (Path): csv file reference

        Returns:
            str: calculated hash value as String
        """
        if csv_file is None:
            raise err.ImportFileDuplicate('Input file not provided')

        with open(csv_file, encoding='ISO-8859-1', mode='r') as csvfile:
            checksum = hashlib.md5(csvfile.read().encode('ISO-8859-1')).hexdigest().upper()
            logger.info("csv hash calculated: %s", checksum)
            return checksum
    
    def read_lines(self, csv_file):
        with open(csv_file, encoding='ISO-8859-1') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            logger.info("reader initialized with encoding: %s", 'ISO-8859-1')
            for row in reader:
                yield row

    def _get_date_object(self, date_str: str) -> datetime:
        raise NotImplementedError('Unspecified date format requested')

    def _make_num(self, value: str) -> float:
        """Providing value as float number for calculation

        Args:
            value (str): Extracted value from Csv file

        Returns:
            float: converted value
        """
        cleaned_string = value
        if '€' in value:
            cleaned_string = value[:-2]
        cleaned_string = cleaned_string.replace(' €', '')
        cleaned_string = cleaned_string.replace('.', '')  # erst die tausender weg
        cleaned_string = cleaned_string.replace(',', '.')
        cleaned_string = ''.join(char for char in cleaned_string if char.isdigit() or char == '-' or char == '.')
        logger.debug("cleaned string: %s", cleaned_string)
        return float(cleaned_string)
    
    def get_meta_data(self, csv_file: pathlib.Path, start_row: int, get_date_object):
        """returns some meta data necessary for creation a history Dataclass instance

        Returns:
            list: list of dictionpories. Every dict should have:
            - 'end_date': datetime object in format '%d.%m.%Y'
            - 'start_date': datetime object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
            - 'file_name': (str) showing the file name
            - 'file_ext': showing the file extension
        """
        CSV_START_ROW = start_row
        meta = cfg.CSV_META.copy()
        meta['checksum'] = self.get_checksum(csv_file)
        meta['file_ext'] = 'csv'
        # Extrahiere den Dateinamen ohne den Pfad und die .csv-Erweiterung
        meta['file_name'] = str(csv_file.stem).replace('.csv', '')
        meta['start_date'] = datetime.strptime('01.01.3000', "%d.%m.%Y")
        meta['end_date'] = datetime.strptime('01.01.1000', "%d.%m.%Y")
        
        for ctr, line in enumerate(self.read_lines(csv_file)):
            if len(line) < 1:
                # skip empty lines
                continue

            if ctr == 0:
                # retrieve the account from the first line
                # meta['account'] = line[1].replace("Girokonto", "").replace("/", "").strip()
                meta['account'] = self.extract_account_or_card_number(line)
            elif ctr > CSV_START_ROW:
                # Datum in der Classic befindet sich in der ersten Spalte
                date_obj = get_date_object(line[0])
                if date_obj:  # Wenn ein gültiges Datum zurückgegeben wurde
                    # Aktualisiere das Startdatum mit dem kleineren der beiden Werte
                    meta['start_date'] = min(meta['start_date'], date_obj)
                    # Aktualisiere das Enddatum mit dem größeren der beiden Werte
                    meta['end_date'] = max(meta['end_date'], date_obj)                
            else:
                logger.warning("No Transaction in the line nr.:: %s", ctr)
        return meta
    
    def extract_account_or_card_number(self, line: list) -> str:
        # Suche nach einer Kontonummer, die mit "DE" beginnt
        for entry in line:
            if "DE" in entry:
                start_idx = entry.find("DE")
                account_number = entry[start_idx:start_idx + 22]  # Nimm die nächsten 22 Zeichen (DE + 20 Ziffern)
                return account_number

            # Wenn "Kreditkarte" im String vorkommt, extrahiere die Kreditkartennummer
            if "Kreditkarte" in entry:
                start_idx = entry.find(":") + 1
                card_number = entry[start_idx:].strip()  # Extrahiere die Kreditkartennummer nach dem ':'
                return card_number

        return None

    def get_transactions_as_list(self, csv_file: pathlib.Path, start_row: int):
        """reads line from CSV file and yields a line as transaction
            If a directory is provided, loops over csv files in the directory
        
        Yields:
            generator: to get the line as a list  for loop is necessary
        """
        with open(csv_file, mode='r', encoding='ISO-8859-15', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for ctr, line in enumerate(reader):
                if ctr > start_row:
                    yield line
    
    def get_tr_value(self, line: list, VALUE: int) -> str:
        value = self._make_num(str(line[VALUE]))
        return value

    def create_history(self, history: dict) -> History:
        """The API is creating a History Dataclass instance,
            which can be used to be imported into DB.
            history needs to have:
            - 'end_date': str object representing a date in a format '%d.%m.%Y'
            - 'start_date': str object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums
              from History table in DB
            - ?
        Args:
            history (dict): data to be used for History creatiion
        Raises:
            err.NoValidHistoryData: if data provided not as dict
        Returns:
            History: History instance
        """
        if isinstance(history, dict):            
            his = History(history['file_name'],
                          history['file_ext'],
                          history['account'],
                          datetime.now(),
                          history['end_date'],
                          history['start_date'],
                          history['checksum'])
        else:
            logger.debug("History is not instance of dict")
            raise err.NoValidHistoryData(f"datum provided with false format: {history}")

        return his
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

 
class ImporterAdapter(a.AbstractInputHandler):
    """Handler class to import data csv file(s)
    """
    csv_hashes = []
    csv_files = []

    def __init__(self, pth):
        if pathlib.Path(pth).is_file():
            self.input = pth
        else:
            # all csv files need to be of the same format. auto detection is not implemented yet.
            # self.csv_files = list(pathlib.Path(pth).glob('**/*.csv'))
            raise err.NoValidInputFilesFound('No valid csv file provided')
        self.classic_input = None
        self.modern_input = None
        self.dcard_input = None 
        self.meta_data = []
        logger.info("CSV Handler initialized")

    def get_meta_from_classic(self):
        if self.classic_input is None:
            self.classic_input = ClassicInput.get_instance(self.input)
        meta_data = self.classic_input.get_meta_data()    
        
        return meta_data
    
    def get_transaction_from_classic(self):
        if self.classic_input is None:
            self.classic_input = ClassicInput.get_instance(self.input)
            self.classic_input.get_meta_data()    
        tr = self.classic_input.get_transaction()
        yield tr

    def get_history_from_classic(self, meta: dict):
        if self.classic_input is None:
            self.classic_input = ClassicInput.get_instance(self.input)
            self.classic_input.get_meta_data()    
        his = self.classic_input.get_history(meta)
        return his

    def get_meta_from_modern(self):
        if self.modern_input is None:
            # self.modern_input = ModernInput(self.input)
            self.modern_input = ModernInput.get_instance(self.input)
        meta_data = self.modern_input.get_meta_data()    
        
        return meta_data

    def get_transaction_from_modern(self):
        if self.modern_input is None:
            self.modern_input = ModernInput.get_instance(self.input)
            self.modern_input.get_meta_data()    
        tr = self.modern_input.get_transaction()
        yield tr

    def get_history_from_modern(self, meta: dict):
        if self.modern_input is None:
            self.modern_input = ClassicInput.get_instance(self.input)
            self.modern_input.get_meta_data()    
        his = self.modern_input.get_history(meta)
        return his

    def get_meta_from_dcard(self):
        if self.dcard_input is None:
            # self.dcard_input = DailyCard(self.input)
            self.dcard_input = DailyCard.get_instance(self.input)
        meta_data = self.dcard_input.get_meta_data()    
        
        return meta_data

    def get_transaction_from_dcard(self):
        if self.dcard_input is None:            
            self.dcard_input = DailyCard.get_instance(self.input)
            self.dcard_input.get_meta_data()    
        tr = self.dcard_input.get_transaction()
        yield tr

    def get_history_from_dcard(self, meta: dict):
        if self.dcard_input is None:
            self.dcard_input = ClassicInput.get_instance(self.input)
            self.dcard_input.get_meta_data()    
        his = self.dcard_input.get_history(meta)
        return his


class ClassicInput(InputMaster, a.HandlerReadIF):
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
    __instance__ = None
   
    def __init__(self, pth: pathlib.Path):
        """
        Process the classic csv input
        """
        self.input = pth
        self.src_account = None

    @staticmethod
    def get_instance(pth: pathlib.Path): 
        """provides instance of the ClassicInput

        Returns:
            ClassicInput (HandlerReadIF): singleton instance
        """
        if ClassicInput.__instance__ is None:
            ClassicInput.__instance__ = ClassicInput(pth)
        return ClassicInput.__instance__
    
    def _get_date_object(self, date_str: str) -> datetime:
        date_obj = None
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise err.InvalidTimeFormat('Classic format provided with incompatible date format')        
        return date_obj
    
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
    
    def _make_transaction(self, line: list) -> Transaction:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        transaction = Transaction(self._get_tr_date(line),
                                  line[self.TEXT],
                                  'not provided',                       # status,
                                  line[self.RECEIVER],
                                  line[self.VERWENDUNG],
                                  line[self.KONTO],
                                  self.get_tr_value(line, self.VALUE),
                                  line[self.DEBITOR_ID],
                                  line[self.MANDATS_REF],
                                  line[self.CUSTOMER_REF],
                                  src_konto)
        return transaction
    
    def get_transaction(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            return self._make_transaction(transrow)
    
    def get_meta_data(self) -> dict:
        """returns some meta data necessary for creation a history Dataclass instance

        Returns:
            list: list of dictionpories. Every dict should have:
            - 'end_date': datetime object in format '%d.%m.%Y'
            - 'start_date': datetime object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
            - 'file_name': (str) showing the file name
            - 'file_ext': showing the file extension
        """
        meta = super().get_meta_data(self.input, self.CSV_START_ROW, self._get_date_object)    
        self.src_account=meta['account']
        return meta
    
    def get_history(self, meta: dict) -> History:
        his = super().create_history(meta)
        return his

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"
    
class ModernInput(InputMaster, a.HandlerReadIF):
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
    __instance__ = None

    def __init__(self, pth: pathlib.Path):
        """
        Process the classic csv input
        """
        self.input = pth
        self.src_account = None

    @staticmethod
    def get_instance(pth: pathlib.Path): 
        """provides instance of the ModernInput

        Returns:
            ModernInput (HandlerReadIF): singleton instance
        """
        if ModernInput.__instance__ is None:
            ModernInput.__instance__ = ModernInput(pth)
        return ModernInput.__instance__
    
    def _get_date_object(self, date_str: str) -> datetime:
        date_obj = None
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%y")
        except ValueError:
            raise err.InvalidTimeFormat('Modern format provided with incompatible date format')        
        return date_obj
    
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
    
    def _make_transaction(self, line: list) -> Transaction:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        transaction = Transaction(self._get_tr_date(line),
                                  'not provided',                       # text,
                                  line[self.STATUS],
                                  line[self.RECEIVER],
                                  line[self.VERWENDUNG],
                                  'not provided',                       # line[self.KONTO] - Kein Konto in Beta?
                                  self.get_tr_value(line, self.VALUE),
                                  line[self.DEBITOR_ID],
                                  line[self.MANDATS_REF],
                                  line[self.CUSTOMER_REF],
                                  src_konto)
        return transaction
    
    def get_transaction(self):
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            return self._make_transaction(transrow)

    def get_meta_data(self) -> dict:
        """returns some meta data necessary for creation a history Dataclass instance

        Returns:
            list: list of dictionpories. Every dict should have:
            - 'end_date': datetime object in format '%d.%m.%Y'
            - 'start_date': datetime object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
            - 'file_name': (str) showing the file name
            - 'file_ext': showing the file extension
        """
        meta = super().get_meta_data(self.input, self.CSV_START_ROW, self._get_date_object)
        self.src_account=meta['account']
        return meta
    
    def get_history(self, meta: dict) -> History:
        his = super().create_history(meta)
        return his
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"

class DailyCard(InputMaster, a.HandlerReadIF):
    DATE = 2
    RECEIVER = 3
    VALUE = 4
    CSV_START_ROW = 6
    __instance__ = None

    def __init__(self, pth: pathlib.Path):
        """
        Process the cradit card csv input
        """
        self.input = pth
        self.src_account = None

    @staticmethod
    def get_instance(pth: pathlib.Path): 
        """provides instance of the DailyCard

        Returns:
            DailyCard (HandlerReadIF): singleton instance
        """
        if DailyCard.__instance__ is None:
            DailyCard.__instance__ = DailyCard(pth)
        return DailyCard.__instance__
    
    def _get_date_object(self, date_str: str) -> datetime:
        date_obj = None
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise err.InvalidTimeFormat('Credit Card format provided with incompatible date format')        
        return date_obj
    
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
  
    def _make_transaction(self, line: list) -> Transaction:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        transaction = Transaction(self._get_tr_date(line),
                                  'not provided',                   # line[self.TEXT],
                                  'not provided',
                                  line[self.RECEIVER],
                                  'not provided',                   # line[self.VERWENDUNG],
                                  'not provided',                   #line[self.KONTO],
                                  self.get_tr_value(line, self.VALUE),
                                  'not provided',                   # line[self.DEBITOR_ID],
                                  'not provided',                   # line[self.MANDATS_REF],
                                  'not provided',                   # line[self.CUSTOMER_REF],
                                  src_konto)
        return transaction
    
    def get_transaction(self):
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            return self._make_transaction(transrow)

    def get_meta_data(self) -> dict:
        """returns some meta data necessary for creation a history Dataclass instance

        Returns:
            list: list of dictionpories. Every dict should have:
            - 'end_date': datetime object in format '%d.%m.%Y'
            - 'start_date': datetime object in format '%d.%m.%Y'
            - 'account': string object showing from which account the data were exported
            - 'checksum': calculated checksum over the csv file to be compared with checksums from History table in DB
            - 'file_name': (str) showing the file name
            - 'file_ext': showing the file extension
        """
        meta = super().get_meta_data(self.input, self.CSV_START_ROW, self._get_date_object)
        self.src_account=meta['account']
        return meta
    
    def get_history(self, meta: dict) -> History:
        his = super().create_history(meta)
        return his
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"

