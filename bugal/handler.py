
"""Handlers
    - xls reades & writer

"""

from dataclasses import fields, asdict
import os
import hashlib
import zipfile
import csv

from openpyxl import Workbook
# from openpyxl.utils import exceptions as openpyxl_exception

from . import cfg


class NoCsvFilesFound(Exception):
    """Exception if in given folder no CSV files could be found"""


class DouplicateCsvFile(Exception):
    """Exception if user try to import the same csv file twice"""


class ExcelWriter():
    """Handler class to print data to excel file
    """

    def __init__(self, xls_file):
        self.xls_file = xls_file
        self.work_book = Workbook()
        self.work_book.iso_dates = True
        self.transactions = []
        self.history = None
        self.rule = None
        self.properties = None
        self.guide = ""

    def print_transactions(self):
        """create transactions sheet and print transaction to the excel
        """
        # create the sheet
        sheet = self.work_book.create_sheet('Transaktionen')

        # print header
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Datum'], value='Datum')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Buchungstext'], value='Buchungstext')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Verwendungszweck'], value='Verwendungszweck')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Kontonummer'], value='Kontonummer')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['BLZ'], value='BLZ')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Betrag'], value='Betrag')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['Checksum'], value='Checksum')
        sheet.cell(row=cfg.MIN_ROW - 1, column=cfg.COLUMNS['vom Konto'], value='vom Konto')
        # print data
        for t_ctr, transaction in enumerate(self.transactions, start=cfg.MIN_ROW):
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Datum'], value=transaction.date)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Buchungstext'], value=transaction.text)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Verwendungszweck'], value=transaction.verwendung)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Kontonummer'], value=transaction.konto)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['BLZ'], value=transaction.blz)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Betrag'], value=transaction.value)
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['Checksum'], value=hash(transaction))
            sheet.cell(row=t_ctr, column=cfg.COLUMNS['vom Konto'], value=transaction.src_konto)

    def print_history(self):
        sheet = self.work_book.create_sheet('Historie')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_rules(self):
        sheet = self.work_book.create_sheet('Regeln')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_properties(self):
        sheet = self.work_book.create_sheet('Properties')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_year(self):
        """Prints an overview for the year to excel
        """
        sheet = self.work_book.create_sheet('Jahr')
        sheet.cell(row=2, column=2, value='not implemented')

    def print_guide(self):
        """prints the users guide to excel

        #     Returns:
        #         None
        """
        guide = """In der Tabelle Transactions findest du alle Transaktionen, die aus der Batenbank exportiert worden sind"""
        sheet = self.work_book.create_sheet('Guide')
        sheet.cell(row=2, column=2, value=guide)

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
                self.work_book.remove('Sheet')
            except ValueError:
                pass
            self.work_book.save(self.xls_file)
            self.work_book.close()
            success = True

            # except PermissionError as permission:
            #     print(f"An error occurred while writing to the Excel file: {permission}, \
            #           please close the excel file and press enter")
            #     input()

        except ValueError as value:
            print(f"An error occurred while writing to the Excel file: {value}")
            self.work_book.close()
        return success


class CSVImporter():
    """Handler class to import data csv file(s)
    """
    csv_hashes = []

    def __init__(self, pth):
        self.pth = pth
        self.invalid_files = []

    def _read_singel_csv(self, fl_pth):
        lines = []
        try:
            with open(fl_pth, newline='', encoding='utf-8') as csvfile:
                checksum = hashlib.md5(csvfile.read()).hexdigest().upper()
                if checksum in self.csv_hashes:
                    raise DouplicateCsvFile
                else:
                    self.csv_hashes.append(checksum)
                reader = csv.reader(csvfile, delimiter=';')
                for _ in range(cfg.CSV_START_ROW):
                    next(reader)
                for line in reader:
                    lines.append(line)
        except UnicodeDecodeError:
            with open(fl_pth, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                for _ in range(cfg.CSV_START_ROW):
                    next(reader)
                for line in reader:
                    lines.append(line)
        except FileNotFoundError:
            self.invalid_files.append(fl_pth)

        return lines

    def get_transactions(self):
        """reads line from CSV file and yields a line as transaction

        Yields:
            list: list from csv data
        """
        lines = []
        if os.path.isfile(self.pth):
            lines.extend(self._read_singel_csv(self.pth))
        else:
            files = list(self.pth.glob('**/*.csv'))
            if len(files) == 0:
                raise cfg.NoCsvFilesFound
            for fl_pth in files:
                lines.extend(self._read_singel_csv(fl_pth))

        for line in lines:
            yield line


class ArtifactHandler():
    """Handles artifacts
    """
    def archive_imports(self, archive, artifact):
        """adds the imported csv file into archive
        """
        with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED) as newzip:
            newzip.write(artifact, arcname=artifact.name)
        artifact.unlink()
