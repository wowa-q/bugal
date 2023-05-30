# pylint: skip-file
# flake8: noqa
from datetime import date
import pathlib
import os

import pytest
from openpyxl import load_workbook
import zipfile

from context import bugal

from bugal import cfg
from bugal import model
from bugal import handler
from bugal.handler import ArtifactHandler
from fixtures import basic
from fixtures import csv_fx
from fixtures.csv_fx import fx_zip_archive

FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

#@pytest.mark.skip()
def test_import_single_csv(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    test_transaction = []
    for transaction in csv_importer.get_transactions():    
        assert transaction is not None, f"transaction not received - None"
        assert isinstance(transaction, list), f"returned transaction is not a list"
        assert transaction != [], f"empty list received for imported transaction"
        if len(test_transaction) == 0:
            test_transaction = transaction.copy()
    
    assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 


# @pytest.mark.skip()
def test_import_banch_csv(fx_banch_of_csv):    
    csv_importer = handler.CSVImporter(fx_banch_of_csv)
    test_transaction = []
    nr_lines = 0
    for transaction in csv_importer.get_transactions():
        assert transaction is not None, f"transaction not received - None"
        assert isinstance(transaction, list), f"returned transaction is not a list"
        assert transaction != [], f"empty list received for imported transaction"
        nr_lines += 1
        if len(test_transaction) == 0:
            test_transaction = transaction.copy()
    
    assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
    assert nr_lines == 15, f"number of transactions is incorrect: {nr_lines} instead of 15"

#@pytest.mark.skip()
def test_skip_invalid_csv(fx_single_invalid_csv, fx_banch_of_invalid_csv):
    csv_importer = handler.CSVImporter('')
    # with pytest.raises(FileNotFoundError):
    #         csv_importer.get_transactions()
    
    # with pytest.raises(cfg.NoCsvFilesFound):
    #         csv_importer.get_transactions()
    csv_importer.get_transactions()
    
    csv_importer = handler.CSVImporter(fx_single_invalid_csv)

    csv_importer = handler.CSVImporter(fx_banch_of_invalid_csv)
    
# @pytest.mark.skip()
def test_csv_archived(fx_banch_of_csv, fx_zip_archive):
    
    art_handler = ArtifactHandler()
    fx_list = fx_banch_of_csv.glob('*.csv')
    for fx_file in fx_list:
        art_handler.archive_imports(archive=fx_zip_archive, artifact=fx_file)
    assert fx_zip_archive.exists() == True, f"No zip archive found {fx_zip_archive}"
    with zipfile.ZipFile(fx_zip_archive, 'r') as newzip:
        file_list = newzip.namelist()
        for fx_file in fx_list:
            assert fx_file in file_list, f"File {fx_file} not found in the archive"

@pytest.mark.skip()
def test_no_import_of_double_csv(fx_single_csv):
    csv_importer1 = handler.CSVImporter(fx_single_csv)
    csv_importer2 = handler.CSVImporter(fx_single_csv)
    test_transaction = []
    for transaction in csv_importer1.get_transactions():
        assert transaction is not None, f"transaction not received - None"
        assert isinstance(transaction, list), f"returned transaction is not a list"
        assert transaction != [], f"empty list received for imported transaction"
        if len(test_transaction) == 0:
            test_transaction = transaction.copy()
    assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
    for transaction in csv_importer2.get_transactions():
        assert transaction is None, f"transactions repeatedly imported"



# @pytest.mark.skip()
# def test_template():
#     assert False, "Not implemented"