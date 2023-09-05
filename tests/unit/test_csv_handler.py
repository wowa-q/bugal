# pylint: skip-file
# flake8: noqa
from datetime import date, datetime
import pathlib
import os
import shutil

import pytest
from openpyxl import load_workbook
import zipfile
import csv 

from context import bugal

from bugal import cfg
from bugal import model
from bugal import handler
from bugal import csv_handler
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

    gen_reader = csv_importer.read_lines(fx_single_csv)
    for ctr, line in enumerate(gen_reader):
        if ctr == 0:
            assert line[0] == "Kontonummer:", f"reader {line[0]}"
        elif ctr == 7:
            assert line[0] == "24.01.2023", f"reader {line[0]}"

# @pytest.mark.skip()
def test_service_callback_classic(fx_single_csv):
    account = ''
    min_date = None
    max_date = None
    for ctr, line in enumerate(csv_handler.read_lines(fx_single_csv)):
        if ctr in[0,2,3,4,6,7,8,9,10,11]:
            assert len(line)>0, f"empty line nr: {ctr}"        
        if ctr in[6,7,8,9,10,11]:
            assert len(line) == 12, f"flase line length line nr: {ctr}"
            date_str = line[0]  
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                continue
            if min_date is None or date_obj < min_date:
                min_date = date_obj
            if max_date is None or date_obj > max_date:
                max_date = date_obj
        if ctr == 0:
            assert len(line) == 3, f"flase line length line nr: {ctr}"            
            account = line[1].replace("Girokonto", "").replace("/", "").strip()
            assert account == 'DE12345300001019363165', f"False account:{account}"
    checksum = csv_handler.get_checksum(fx_single_csv)
    assert len(checksum) == 32, f"{checksum}" # '5BEE30D0ECA3B77D4CC447CE7E52EA69'
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert min_date == datetime.strptime('16.01.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
    assert max_date == datetime.strptime('24.01.2023', "%d.%m.%Y"), f"min. Datum falsch {max_date}"
    
# @pytest.mark.skip()
def test_service_callback_beta(fx_single_csv_new):
    account = ''
    min_date = None
    max_date = None
    for ctr, line in enumerate(csv_handler.read_lines(fx_single_csv_new)):
        if ctr in[0,2,4,6,7,8,9,10,11]:
            assert len(line)>0, f"empty line nr: {ctr}"
        if ctr in[4,5,6,7,8,9,10,11]:
            assert len(line) == 12, f"flase line length line nr: {ctr}"
            date_str = line[0]
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                continue
            if min_date is None or date_obj < min_date:
                min_date = date_obj
            if max_date is None or date_obj > max_date:
                max_date = date_obj
        if ctr == 0:
            assert len(line) == 3, f"flase line length line nr: {ctr}"
            account = line[1].replace("Girokonto", "").replace("/", "").strip()
            assert account == 'DE12345300001019363165', f"False account:{account}"
    checksum = csv_handler.get_checksum(fx_single_csv_new)
    assert len(checksum) == 32, f"{checksum}" #'E10D5AEEEEF8BE6D336705A7FAE1CC83'
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert max_date == datetime.strptime('24.02.2023', "%d.%m.%Y"), f"max. Datum falsch {max_date}"
    assert min_date == datetime.strptime('24.01.2022', "%d.%m.%Y"), f"min. Datum falsch {min_date}"

# @pytest.mark.skip()
def test_get_meta_classic(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    meta = csv_importer._get_meta_data(fx_single_csv)
    assert len(meta['checksum']) == 32, f"Checksum: {meta['checksum']}" #  '5BEE30D0ECA3B77D4CC447CE7E52EA69'
    assert meta['file_ext'] == 'csv'
    # assert meta['file_name'] == 'D:\\projects\910_prProjects\bugal\tests\fixtures\single', f"File name: {meta['file_name']}"
    assert meta['account'] == 'DE12345300001019363165', f"Account: {meta['account']}"
    min_date = meta['start_date']
    max_date = meta['end_date']
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert min_date == datetime.strptime('16.01.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
    assert max_date == datetime.strptime('24.01.2023', "%d.%m.%Y"), f"min. Datum falsch {max_date}"

# @pytest.mark.skip()
def test_get_meta_beta(fx_single_csv_new):
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    csv_importer.input_type = cfg.TransactionListBeta
    meta = csv_importer._get_meta_data(fx_single_csv_new)
    assert len(meta['checksum']) == 32 , f"Checksum: {meta['checksum']}" # 'E10D5AEEEEF8BE6D336705A7FAE1CC83'
    assert meta['file_ext'] == 'csv'
    # assert meta['file_name'] == 'D:\\projects\910_prProjects\bugal\tests\fixtures\single', f"File name: {meta['file_name']}"
    assert meta['account'] == 'DE12345300001019363165', f"Account: {meta['account']}"
    min_date = meta['start_date']
    max_date = meta['end_date']
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert min_date == datetime.strptime('24.01.2022', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
    assert max_date == datetime.strptime('24.02.2023', "%d.%m.%Y"), f"max. Datum falsch {max_date}"

# @pytest.mark.skip()
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

# @pytest.mark.skip()
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
    
    art_handler = ArtifactHandler(fx_zip_archive)
    fx_list = fx_banch_of_csv.glob('*.csv')
    for fx_file in fx_list:
        art_handler.archive_imports(artifact=fx_file)
    assert fx_zip_archive.exists() == True, f"No zip archive found {fx_zip_archive}"
    with zipfile.ZipFile(fx_zip_archive, 'r') as newzip:
        file_list = newzip.namelist()
        for fx_file in fx_list:
            assert fx_file in file_list, f"File {fx_file} not found in the archive"


# @pytest.mark.skip()
# def test_template():
#     assert False, "Not implemented"