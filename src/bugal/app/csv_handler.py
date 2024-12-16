"""
Gehört zu busines layer. spezialisierter Handler.
Soll keine model spezifische Datentypen verwenden. 
Es ist die Aufgabe des Stacks die Datentypen in Dataclass umzuwandeln
"""
import os
import pathlib
import hashlib
import csv
from datetime import datetime
import logging


# from bugal import cfg
from . import bugal_if as a
from cfg import config as cfg
from libs import exceptions as err


logger = logging.getLogger(__name__)


class InputMaster():
    """ Provides generic operations - must not be used outside of 
        handler implementation.
    """
    # Reviewed
    def get_checksum(self, csv_file: pathlib.Path):
        """provides hash value for csv file

        Args:
            csv_file (Path): csv file reference

        Returns:
            str: calculated hash value as String
        """
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
    # Reviewed
    def _get_date_object(self, date_str: str) -> datetime:
        try:
            # Versuche das erste Format
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            try:
                # Falls das erste Format fehlschlägt, versuche das zweite Format
                date_obj = datetime.strptime(date_str, "%d.%m.%y")
            except ValueError:
                # Wenn beide fehlschlagen, wirf eine benutzerdefinierte Ausnahme
                raise err.InvalidTimeFormat(f'Classic format provided with incompatible date format: {date_str}')
        return date_obj
    # Reviewed
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
    # Reviewed
    def get_meta_data(self, csv_file: pathlib.Path, start_row: int, get_date_object) -> dict:
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
    # Reviewed    
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
    # Reviewed
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
    # Reviewed
    def get_tr_value(self, tran: dict) -> float:
    # def get_tr_value(self, line: list, VALUE: int) -> float:
        # value = self._make_num(str(line[VALUE]))
        value = self._make_num(tran.get('value'))
        return value    
    # Reviewed
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

 
class Importer():
    """
    """

    def __init__(self):
        def __init__(self, adapter: a.ICSVAdapter):
            self.adapter = adapter
    #TODO: die funtkion für die benutzung anpassen. Das Model sucht den passenden Adapter aus
    def read(self, file_path: str):
        """import by using the adapter

        Args:
            file_path (str): _description_

        Returns:
            List[Dict[str, str]]: _description_
        """
        return self.adapter.process_csv(file_path)


class ClassicInputAdapter(InputMaster, a.ICSVAdapter):
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
        """provides instance of the ClassicInputAdapter

        Returns:
            ClassicInputAdapter (ICSVAdapter): singleton instance
        """
        if ClassicInputAdapter.__instance__ is None:
            ClassicInputAdapter.__instance__ = ClassicInputAdapter(pth)
        return ClassicInputAdapter.__instance__
    # Reviewed
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
    # Reviewed
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
    # Reviewed - wird das gebraucht oder kommt Stack auch so zurecht?
    def _make_transaction(self, line: list) -> dict:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        
        transaction = cfg.META_TRANSACTION.copy()
        transaction['tdate'] = line[self.DATE]
        transaction['text'] = line[self.TEXT]
        transaction['status'] = 'not provided'
        transaction['receiver'] = line[self.RECEIVER]
        transaction['verwendung'] = line[self.VERWENDUNG]
        transaction['konto'] = line[self.KONTO]
        transaction['value'] = line[self.VALUE]
        transaction['debitor_id'] = line[self.DEBITOR_ID]
        transaction['mandats_ref'] = line[self.MANDATS_REF]
        transaction['customer_ref'] = line[self.CUSTOMER_REF]
        transaction['src_konto'] = src_konto
        
        return transaction
    
    def get_transaction(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            # return self._make_transaction(transrow)
            temp_dict = cfg.META_TRANSACTION.copy()
            if len(transrow) < 7:
                self.logger.debug("#Data provided has not correct length: %s", len(transrow))
                print(f'###  has not correct length: {transrow} ###')
                raise err.NoValidTransactionData(f'Model: Transaction data list to short: {len(transrow)}')
            temp_dict['tdate'] = transrow[self.DATE]
            temp_dict['text'] = transrow[self.TEXT]
            temp_dict['status'] = ''
            temp_dict['debitor'] = transrow[self.RECEIVER]
            temp_dict['verwendung'] = transrow[self.VERWENDUNG]
            temp_dict['value'] = transrow[self.VALUE]
            temp_dict['debitor_id'] = transrow[self.DEBITOR_ID]
            temp_dict['mandats_ref'] = transrow[self.MANDATS_REF]
            temp_dict['customer_ref'] = transrow[self.CUSTOMER_REF]
            
            yield temp_dict

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"


class ModernInputAdapter(InputMaster, a.ICSVAdapter):
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
        if ModernInputAdapter.__instance__ is None:
            ModernInputAdapter.__instance__ = ModernInputAdapter(pth)
        return ModernInputAdapter.__instance__
    
    # def _get_date_object(self, date_str: str) -> datetime:
    #     date_obj = None
    #     try:
    #         date_obj = datetime.strptime(date_str, "%d.%m.%y")
    #     except ValueError:
    #         raise err.InvalidTimeFormat('Modern format provided with incompatible date format')        
    #     return date_obj
    
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
    
    # Reviewed - wird das gebraucht oder kommt Stack auch so zurecht?
    def _make_transaction(self, line: list) -> dict:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        
        transaction = cfg.TRANSACTION.copy()
        transaction['date'] = self._get_tr_date(line)
        transaction['text'] = line[self.TEXT]
        transaction['status'] = 'not provided'
        transaction['receiver'] = line[self.RECEIVER]
        transaction['verwendung'] = line[self.VERWENDUNG]
        transaction['konto'] = line[self.KONTO]
        transaction['value'] = self.get_tr_value(line, self.VALUE)
        transaction['debitor_id'] = line[self.DEBITOR_ID]
        transaction['mandats_ref'] = line[self.MANDATS_REF]
        transaction['customer_ref'] = line[self.CUSTOMER_REF]
        transaction['src_konto'] = src_konto
        
        return transaction
    
    def get_transaction(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            # return self._make_transaction(transrow)
            return transrow

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
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"


class ModernInput_2024Adapter(InputMaster, a.ICSVAdapter):
    """Works for format from 2024, including Tagesgeldkonto

    """
    DATE = 0
    STATUS = 2
    SENDER = 3
    RECEIVER = 4
    VERWENDUNG = 5
    VALUE = 8
    DEBITOR_ID = 9
    MANDATS_REF = 10
    CUSTOMER_REF = 11
    CSV_START_ROW = 5
    __instance__ = None

    def __init__(self, pth: pathlib.Path):
        """
        Process the classic csv input
        """
        self.input = pth
        self.src_account = None

    @staticmethod
    def get_instance(pth: pathlib.Path):
        """provides instance of the ModernInput_2024Adapter

        Returns:
            ModernInput_2024Adapter (ICSVAdapter): singleton instance
        """
        if ModernInput_2024Adapter.__instance__ is None:
            ModernInput_2024Adapter.__instance__ = ModernInput_2024Adapter(pth)
        return ModernInput_2024Adapter.__instance__
    
    def get_transaction(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            # return self._make_transaction(transrow)
            temp_dict = cfg.META_TRANSACTION.copy()
            if len(transrow) < 7:
                logger.debug("#Data provided has not correct length: %s", len(transrow))
                print(f'###  has not correct length: {transrow} ###')
                raise err.NoValidTransactionData(f'Model: Transaction data list to short: {len(transrow)}')
            temp_dict['tdate'] = transrow[self.DATE]
            temp_dict['text'] = ''
            temp_dict['status'] = transrow[self.STATUS]
            temp_dict['debitor'] = transrow[self.RECEIVER]
            temp_dict['verwendung'] = transrow[self.VERWENDUNG]
            temp_dict['value'] = transrow[self.VALUE]
            temp_dict['debitor_id'] = transrow[self.DEBITOR_ID]
            temp_dict['mandats_ref'] = transrow[self.MANDATS_REF]
            temp_dict['customer_ref'] = transrow[self.CUSTOMER_REF]
            
            yield temp_dict

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"
    

class DailyCardAdapter(InputMaster, a.ICSVAdapter):
    DATE = 0
    STATUS = 2
    TYPE = 4
    RECEIVER = 3
    VALUE = 5
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
        if DailyCardAdapter.__instance__ is None:
            DailyCardAdapter.__instance__ = DailyCardAdapter(pth)
        return DailyCardAdapter.__instance__
    
    # Inputmaster covers this
    # def _get_date_object(self, date_str: str) -> datetime:
    #     date_obj = None
    #     try:
    #         date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    #     except ValueError:
    #         raise err.InvalidTimeFormat('Credit Card format provided with incompatible date format')        
    #     return date_obj
    
    def _get_tr_date(self, line: list) -> datetime:
        date_string = line[self.DATE]
        date_obj = self._get_date_object(date_string)
        return date_obj
  
    # Reviewed - wird das gebraucht oder kommt Stack auch so zurecht?
    def _make_transaction(self, line: list) -> dict:
        if self.src_account is not None:
            src_konto = self.src_account
        else:
            raise err.NoValidTransactionData('source account not provided')
        
        transaction = cfg.TRANSACTION.copy()
        transaction['date'] = self._get_tr_date(line)
        transaction['text'] = line[self.TEXT]
        transaction['status'] = 'not provided'
        transaction['receiver'] = line[self.RECEIVER]
        transaction['verwendung'] = line[self.VERWENDUNG]
        transaction['konto'] = line[self.KONTO]
        transaction['value'] = self.get_tr_value(line, self.VALUE)
        transaction['debitor_id'] = line[self.DEBITOR_ID]
        transaction['mandats_ref'] = line[self.MANDATS_REF]
        transaction['customer_ref'] = line[self.CUSTOMER_REF]
        transaction['src_konto'] = src_konto
        
        return transaction
    
    def get_transaction(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            # return self._make_transaction(transrow)
            temp_dict = cfg.META_TRANSACTION.copy()
            if len(transrow) < 7:
                self.logger.debug("#Data provided has not correct length: %s", len(transrow))
                print(f'###  has not correct length: {transrow} ###')
                raise err.NoValidTransactionData(f'Model: Transaction data list to short: {len(transrow)}')
            temp_dict['tdate'] = transrow[self.DATE]
            temp_dict['text'] = 'DAILY-CARD'
            temp_dict['status'] = transrow[self.STATUS]
            temp_dict['debitor'] = transrow[self.RECEIVER]
            temp_dict['verwendung'] = transrow[self.TYPE]
            temp_dict['value'] = transrow[self.VALUE]
            temp_dict['debitor_id'] = ''
            temp_dict['mandats_ref'] = ''
            temp_dict['customer_ref'] = ''
            
            yield temp_dict

    def get_transaction_old(self):
        """Must not be executed before get_meta_data, otherwise account is not set properly

        Yields:
            Transaction: Transaction object to be pushed into db
        """
        for _, transrow in enumerate(self.get_transactions_as_list(self.input, self.CSV_START_ROW)):
            # return self._make_transaction(transrow)
            return transrow

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
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}  located in {self.input}"


#       *** PUBLIC APIs ***
def read_lines(csv_file):
    with open(csv_file, encoding='ISO-8859-1') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            yield row

def get_checksum(csv_file):
    with open(csv_file, encoding='ISO-8859-1') as csvfile:
        checksum = hashlib.md5(csvfile.read().encode('ISO-8859-1')).hexdigest().upper()
        return checksum