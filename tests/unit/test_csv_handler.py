# pylint: skip-file
# flake8: noqa
from datetime import date
import pathlib
import os
import csv

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


# @pytest.mark.skip()
def test_read_single_csv(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    test_transaction = []
    with open(fx_single_csv, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter = ';')
        
        for ctr, line in enumerate(reader):
            if ctr == 0:
                assert len(line) > 0, f"Empty line was given"
                assert line[0] == "Kontonummer:", f"reader {line}"
            elif ctr == 7:
                assert line[0] == "24.01.2023", f"reader {line[0]}"

    gen_reader = csv_importer.read_csv(fx_single_csv)
    for ctr, line in enumerate(gen_reader):
        if ctr == 0:
            assert line[0] == "Kontonummer:", f"reader {line[0]}"
        elif ctr == 7:
            assert line[0] == "24.01.2023", f"reader {line[0]}"


#@pytest.mark.skip()
def test_import_single_csv(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    test_transaction = []
    for ctr, csv_output in enumerate(csv_importer.get_transactions()):
        if ctr == 7:
            assert csv_output[1] is not None, f"transaction not received - None"
            assert isinstance(csv_output[1], list), f"returned transaction is not a list"
            assert csv_output[1] != [], f"empty list received for imported transaction"
            
            test_transaction = csv_output[1].copy()
            assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 


# @pytest.mark.skip()
def test_import_banch_csv(fx_banch_of_csv):    
    csv_importer = handler.CSVImporter(fx_banch_of_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    test_transaction = []
    nr_lines = 0
    for ctr, csv_output in enumerate(csv_importer.get_transactions()):
        if ctr == 7:
            assert csv_output[1] is not None, f"transaction not received - None"
            assert isinstance(csv_output[1], list), f"returned transaction is not a list"
            assert csv_output[1] != [], f"empty list received for imported transaction"
            
            test_transaction = csv_output[1].copy()
            assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
            # assert nr_lines == 15, f"number of transactions is incorrect: {nr_lines} instead of 15"

#@pytest.mark.skip()
def test_skip_invalid_csv(fx_single_invalid_csv, fx_banch_of_invalid_csv):
    csv_importer = handler.CSVImporter('')
    # with pytest.raises(FileNotFoundError):
    #         csv_importer.get_transactions()
    
    # with pytest.raises(cfg.NoCsvFilesFound):
    #         csv_importer.get_transactions()
    csv_importer.input_type = cfg.TransactionListClassic
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


# @pytest.mark.skip()
def test_support_new_csv_format(fx_single_csv_new):
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    csv_importer.input_type = cfg.TransactionListBeta
    test_transaction = []

    for ctr, csv_output in enumerate(csv_importer.get_transactions()):
        if ctr == 7:
            assert csv_output[1] is not None, f"transaction not received - None"
            assert isinstance(csv_output[1], list), f"returned transaction is not a list"
            assert csv_output[1] != [], f"empty list received for imported transaction"
            
            test_transaction = csv_output.copy()
            assert test_transaction[0] == "24.01.2022", f"transaction hat falschen Wert {test_transaction}" 

    

# @pytest.mark.skip()
# def test_template():
#     assert False, "Not implemented"