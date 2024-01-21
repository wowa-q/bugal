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
from bugal import exceptions as err
from bugal import model
from bugal import handler
from bugal import csv_handler
from bugal.handler import ArtifactHandler
from fixtures import basic
from fixtures import csv_fx
from fixtures.csv_fx import fx_zip_archive

FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

# pytest.mark.skip()
@pytest.mark.parametrize("csv_fixture, expected", [
    ('beta', cfg.TransactionListBeta),  
    ('classic', cfg.TransactionListClassic),   
])
def test_init_csv_handler(csv_fixture, expected, fx_single_csv, fx_single_csv_new):
    if csv_fixture == 'classic':        
        h = handler.CSVImporter(fx_single_csv)        
        # assert h.input_type == cfg.TransactionListClassic, "input type"
    elif csv_fixture == 'beta':
        h = handler.CSVImporter(fx_single_csv_new, cfg.TransactionListBeta)        
        # assert hb.input_type == cfg.TransactionListBeta, "input type"
    assert h is not None
    assert len(h.csv_files) == 1, "number of csv file is incorect"
    assert h.input_type is not None, "input type"
    h.input_type = None
    with pytest.raises(err.NoInputTypeSet):
        for n in h.get_transactions():
            pass
    with pytest.raises(err.NoInputTypeSet):
        h.get_meta_data()

#@pytest.mark.skip()
def test_read_single_csv(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic

    gen_reader = csv_importer.read_lines(fx_single_csv)
    for ctr, line in enumerate(gen_reader):
        if ctr == 0:
            assert line[0] == "Kontonummer:", f"reader {line[0]}"
        elif ctr == 7:
            assert line[0] == "24.01.2023", f"reader {line[0]}"

#@pytest.mark.skip()
def test_read_single_csv_beta(fx_single_csv_new):
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    csv_importer.input_type = cfg.TransactionListBeta

    gen_reader = csv_importer.read_lines(fx_single_csv_new)
    for ctr, line in enumerate(gen_reader):
        if ctr == 0:
            assert line[0] == "Konto", f"reader {line[0]}"
        elif ctr == 7:
            assert line[0] == "17.10.23", f"reader {line[0]}"

#@pytest.mark.skip()
def test_service_callback_classic(fx_single_csv):
    account = ''
    min_date = None
    max_date = None
    for ctr, line in enumerate(csv_handler.read_lines(fx_single_csv)):
        if ctr in[0,2,3,4,6,7,8,9,10,11]:
            assert len(line)>0, f"empty line nr: {ctr}"        
        if ctr in[6,7,8,9,10,11]:

            date_str = line[0]  
            try:
                if len(date_str) == 8:
                    date_obj = datetime.strptime(date_str, "%d.%m.%y")
                elif len(date_str) == 10:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                else:
                    continue
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
    assert min_date != max_date, f"{min_date}"
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert min_date == datetime.strptime('16.01.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
    assert max_date == datetime.strptime('24.01.2023', "%d.%m.%Y"), f"min. Datum falsch {max_date}"
    
#@pytest.mark.skip()
def test_service_callback_beta(fx_single_csv_new):
    account = ''
    min_date = None
    max_date = None
    for ctr, line in enumerate(csv_handler.read_lines(fx_single_csv_new)):
        if ctr in[0,2,4,6,7,8,9,10,11]:
            assert len(line)>0, f"empty line nr: {ctr}"
        if ctr in[4,5,6,7,8,9,10,11]:
            date_str = line[0]
            try:
                if len(date_str) == 8:
                    date_obj = datetime.strptime(date_str, "%d.%m.%y")
                elif len(date_str) == 10:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                else:
                    continue
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
    assert min_date is not None, f"Min date not updated:{min_date}"
    assert max_date is not None, f"Max date not updated:{min_date}"
    assert len(checksum) == 32, f"{checksum}" #'E10D5AEEEEF8BE6D336705A7FAE1CC83'
    assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
    assert max_date == datetime.strptime('19.10.2023', "%d.%m.%Y"), f"max. Datum falsch {max_date}"
    assert min_date == datetime.strptime('14.10.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"

#@pytest.mark.skip()
def test_get_meta_classic(fx_single_csv):
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    metas = csv_importer.get_meta_data()
    for meta in metas:
        assert len(meta['checksum']) == 32, f"Checksum: {meta['checksum']}" #  '5BEE30D0ECA3B77D4CC447CE7E52EA69'
        assert meta['file_ext'] == 'csv'
        # assert meta['file_name'] == 'D:\\projects\910_prProjects\bugal\tests\fixtures\single', f"File name: {meta['file_name']}"
        assert meta['account'] == 'DE12345300001019363165', f"Account: {meta['account']}"
        min_date = meta['start_date']
        max_date = meta['end_date']
        assert min_date < max_date, f"Datum falsch {min_date} / {max_date}"
        assert min_date == datetime.strptime('16.01.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
        assert max_date == datetime.strptime('24.01.2023', "%d.%m.%Y"), f"min. Datum falsch {max_date}"

#@pytest.mark.skip()
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
    assert min_date == datetime.strptime('14.10.2023', "%d.%m.%Y"), f"min. Datum falsch {min_date}"
    assert max_date == datetime.strptime('19.10.2023', "%d.%m.%Y"), f"max. Datum falsch {max_date}"

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

#@pytest.mark.skip()
def test_import_single_csv_beta(fx_single_csv_new):
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    csv_importer.input_type = cfg.TransactionListBeta
    for ctr, transaction_c in enumerate(csv_importer.get_transactions(), 1):
        assert transaction_c is not None
        for _ctr, csv_output in enumerate(transaction_c, 1):
            if _ctr == 7:
                continue

    assert len(csv_output) > 0, "test transaction not updated"
    assert csv_output[1] != [], f"empty list received for imported transaction"
    assert csv_output[1] == "17.10.23", f"transaction hat falschen Wert {csv_output[1]}"
    assert csv_output[2] == "Gebucht", f"transaction hat falschen Wert {csv_output[2]}"
    assert csv_output[7] == '2.228,57\xa0\x80', f"transaction hat falschen Wert {csv_output[7]}"

#@pytest.mark.skip()
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

@pytest.mark.skip()
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

#@pytest.mark.skip()
def test_artifact_handler_initialization(fx_zip_archive, fx_zip_archive_configured):
    art1 = ArtifactHandler(fx_zip_archive_configured)
    assert art1 is not None    
    assert art1.archive is not None, "archive = None"

    art2 = ArtifactHandler(fx_zip_archive)
    assert art2 is not None    
    assert art2.archive is not None, "archive = None"

# @pytest.mark.skip()
# def test_csv_archived(fx_banch_of_csv, fx_zip_archive):
    
#     art_handler = ArtifactHandler(fx_zip_archive)
#     fx_list = fx_banch_of_csv.glob('*.csv')
#     for fx_file in fx_list:
#         art_handler.archive_imports(artifact=fx_file)
#     assert fx_zip_archive.exists() == True, f"No zip archive found {fx_zip_archive}"
#     with zipfile.ZipFile(fx_zip_archive, 'r') as newzip:
#         file_list = newzip.namelist()
#         for fx_file in fx_list:
#             assert fx_file in file_list, f"File {fx_file} not found in the archive"

# @pytest.mark.skip()
@pytest.mark.parametrize("csv_fixture, expected", [
    ('beta', None),  # 5 number of transactions
    ('classic', None),   # 5 number of transactions
])
def test_raise_broken_date(fx_csv_broken_date_classic, fx_csv_broken_date_beta, csv_fixture, expected):
    stack=model.Stack(cfg.TransactionListClassic) 
    if csv_fixture == 'classic':
        stack.input_type = cfg.TransactionListClassic
        single_csv_1 = fx_csv_broken_date_classic
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListClassic
        
    elif csv_fixture == 'beta':
        stack.input_type = cfg.TransactionListBeta
        single_csv_1 = fx_csv_broken_date_beta
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListBeta
        
    else:
        assert False, "Invalid Parameter"

    with pytest.raises(ValueError):
        meta = csv_importer1._get_meta_data(single_csv_1)


# @pytest.mark.skip()
# def test_template():
#     assert False, "Not implemented"