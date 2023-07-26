"""Handlers
    - xls reades & writer
    - csv importer
    - artifact handler
"""

# from dataclasses import fields, asdict
import os
import hashlib
import zipfile
import csv
from datetime import date, datetime

from openpyxl import Workbook
# from openpyxl.utils import exceptions as openpyxl_exception

from . import cfg
from . import abstract as a


class NoCsvFilesFound(Exception):
    """Exception if in given folder no CSV files could be found"""


class DouplicateCsvFile(Exception):
    """Exception if user try to import the same csv file twice"""


class ExcelWriter(a.HandlerWriteIF):
    """Handler class to print data to excel file
    """

    def __init__(self, xls_file):
        self.xls_file = xls_file
        self._work_book = Workbook()
        self._work_book.iso_dates = True
        self.transactions = []
        self.history = None
        self.rule = None
        self.properties = None
        self.guide = ""

    def print_transactions(self):
        """create transactions sheet and print transaction to the excel
        """
        # create the sheet
        sheet = self._work_book.create_sheet('Transaktionen')

        # print header
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Datum'], value='Datum')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Buchungstext'], value='Buchungstext')
        # pylint: disable=C0301
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Verwendungszweck'], value='Verwendungszweck')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Kontonummer'], value='Kontonummer')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Status'], value='Status')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Betrag'], value='Betrag')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Checksum'], value='Checksum')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['vom Konto'], value='vom Konto')
        # print data
        for t_ctr, transaction in enumerate(self.transactions, start=cfg.MIN_ROW):
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Datum'], value=transaction.date)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Buchungstext'], value=transaction.text)
            # pylint: disable=C0301
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Verwendungszweck'], value=transaction.verwendung)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Kontonummer'], value=transaction.konto)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Status'], value=transaction.status)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Betrag'], value=transaction.value)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Checksum'], value=hash(transaction))
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['vom Konto'], value=transaction.src_konto)

    def print_history(self):
        """Print history to excel
        """
        sheet = self._work_book.create_sheet('Historie')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_rules(self):
        """Print rules to excel
        """
        sheet = self._work_book.create_sheet('Regeln')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_properties(self):
        """Print Properties to Excel
        """
        sheet = self._work_book.create_sheet('Properties')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_year(self):
        """Prints an overview for the year to excel
        """
        sheet = self._work_book.create_sheet('Jahr')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_guide(self):
        """prints the users guide to excel

        #     Returns:
        #         None
        """
        guide = """
                In der Tabelle Transactions findest du alle Transaktionen,
                die aus der Batenbank exportiert worden sind"""
        sheet = self._work_book.create_sheet('Guide')
        sheet.cell(row=2, column=2, value=guide)

    def print(self):
        return self.write_all_to_excel()

    def write_all_to_excel(self):
        """Creates sheets for all relevant data (transactions,
                                                history,
                                                rules,
                                                properties,
                                                guide,
                                                year),
        #     and prints the data to the Excel workbook.

        #     Returns:
        #         bool: True, when writing was siccessful
        """

        success = False

        try:
            for method_name in ['print_transactions',
                                'print_history',
                                'print_properties',
                                'print_guide',
                                'print_rules',
                                'print_year']:
                method = getattr(self, method_name)
                method()
            try:
                self._work_book.remove('Sheet')
            except ValueError:
                pass
            self._work_book.save(self.xls_file)
            self._work_book.close()
            success = True

            # except PermissionError as permission:
            #     print(f"An error occurred while writing to the Excel file: {permission}, \
            #           please close the excel file and press enter")
            #     input()

        except ValueError as value:
            print(f"An error occurred while writing to the Excel file: {value}")
            self._work_book.close()
        return success


class CSVImporter(a.HandlerReadIF):
    """Handler class to import data csv file(s)
    """
    csv_hashes = []

    def __init__(self, pth):
        self.pth = pth
        self.invalid_files = []
        self.meta_data = []
        self.input_type = None

    # not tested
    def get_meta_data(self):
        if os.path.isfile(self.pth):
            self.meta_data.append(self._get_meta_data(self.pth))
        else:
            files = list(self.pth.glob('**/*.csv'))
            for fl_pth in files:
                self.meta_data.append(self._get_meta_data(fl_pth))
        return self.meta_data

    def _get_meta_data(self, csv_file):
        if self.input_type is None:
            raise cfg.NoInputTypeSet
        meta = cfg.CSV_META.copy()
        meta['checksum'] = self.get_checksum(csv_file)
        meta['file_ext'] = 'csv'
        meta['file_name'] = str(csv_file).strip('.csv')
        # with open(csv_file, encoding='ISO-8859-1') as csvfile:
        #     reader = csv.reader(csvfile, delimiter=';')

        #     for ctr, line in enumerate(reader):
        #         if ctr == 0:
        #             meta['account'] = line[1].replace("Girokonto", "").replace("/", "").strip()
        for ctr, line in enumerate(self.read_lines(csv_file)):
            if ctr == 0:
                meta['account'] = line[1].replace("Girokonto", "").replace("/", "").strip()
            if ctr > 5:
                date_str = line[0]
                try:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                except ValueError:
                    continue
                if meta['start_date'] is None or date_obj < meta['start_date']:
                    meta['start_date'] = date_obj
                if meta['end_date'] is None or date_obj > meta['end_date']:
                    meta['end_date'] = date_obj
        return meta

    def read_lines(self, csv_file):
        with open(csv_file, encoding='ISO-8859-1') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                yield row

    def get_checksum(self, csv_file):
        with open(csv_file, encoding='ISO-8859-1') as csvfile:
            checksum = hashlib.md5(csvfile.read().encode('ISO-8859-1')).hexdigest().upper()
            return checksum
    # not tested
    def _get_meta_data_old(self, csv_file) -> dict:
        if self.input_type is None:
            raise cfg.NoInputTypeSet
        meta = cfg.CSV_META.copy()
        for ctr, row in enumerate(self._read_lines(csv_file)):
            if ctr == 0:
                meta['account'] = row[1]
            if ctr > self.input_type.CSV_START_ROW:
                if meta['start_date'] > row[0]:
                    meta['start_date'] = row[0]
                if meta['end_date'] < row[0]:
                    meta['end_date'] = row[0]

        meta['file_name'] = ''
        meta['file_ext'] = 'csv'
        meta['checksum'] = self._get_checksum(csv_file)
        return meta

    def _read_singel_csv(self, fl_pth):

        if self.input_type is None:
            raise cfg.NoInputTypeSet

        lines = []
        meta = cfg.CSV_META.copy()
        meta['file_ext'] = 'csv'
        try:
            with open(fl_pth, newline='', encoding='utf-8') as csvfile:
                meta['file_name'] = fl_pth
                checksum = hashlib.md5(csvfile.read()).hexdigest().upper()
                meta['checksum'] = checksum
                if checksum in self.csv_hashes:
                    raise DouplicateCsvFile
                else:
                    self.csv_hashes.append(checksum)
                reader = csv.reader(csvfile, delimiter=';')
                for _ in range(self.input_type.CSV_START_ROW.value):
                    next(reader)
                for line in reader:
                    lines.append(line)
        except UnicodeDecodeError:
            # with open(fl_pth, newline='', encoding='ISO-8859-1') as csvfile:
            with open(fl_pth, 'rb') as csvfile:
                checksum = hashlib.md5(csvfile.read()).hexdigest().upper()
                if checksum in self.csv_hashes:
                    raise DouplicateCsvFile
                else:
                    self.csv_hashes.append(checksum)
                reader = csv.reader(csvfile, delimiter=';')
                for _ in range(self.input_type.CSV_START_ROW.value):
                    next(reader)
                for line in reader:
                    lines.append(line)
        except FileNotFoundError:
            self.invalid_files.append(fl_pth)

        return lines

    def get_transactions_old(self):
        """reads line from CSV file and yields a line as transaction

        Raises:
            DouplicateCsvFile: _description_

        Yields:
            list: list from csv data
        """
        lines = []
        if os.path.isfile(self.pth):
            lines.extend(self._read_singel_csv(self.pth))
        else:
            files = list(self.pth.glob('**/*.csv'))
            if len(files) == 0:
                raise NoCsvFilesFound
            for fl_pth in files:
                lines.extend(self._read_singel_csv(fl_pth))

        for line in lines:
            yield line

    def read_csv(self, csv_file):
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for line in reader:
                yield line


    def get_transactions(self):
        """NOT TESTED function - alternativ implementation with nested functions

        Raises:
            DouplicateCsvFile: _description_

        Yields:
            _type_: _description_
        """
        if self.input_type is None:
            raise cfg.NoInputTypeSet
        
        files = list(self.pth.glob('**/*.csv'))

        def read_lines(csv_file):
            transaction = []
            account = ''
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                checksum = hashlib.md5(csvfile.read()).hexdigest().upper()
                if checksum in self.csv_hashes:
                    raise DouplicateCsvFile
                else:
                    self.csv_hashes.append(checksum)
                reader = csv.reader(csvfile, delimiter=';')
                # for _ in range(self.input_type.CSV_START_ROW.value):
                #     next(reader)
                # for line in reader:
                #     yield line
                for ctr, line in enumerate(reader):
                    if ctr == 0:
                        account = line[1]                    
                    elif ctr > self.input_type.CSV_START_ROW.value:
                        transaction = line
                        
                    yield [account, transaction]

        for csv_file in files:
            yield read_lines(csv_file)


class ArtifactHandler():
    """Handles artifacts
    """
    def archive_imports(self, archive, artifact):
        """adds the imported csv file into archive
        """
        with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED) as newzip:
            newzip.write(artifact, arcname=artifact.name)
        artifact.unlink()
