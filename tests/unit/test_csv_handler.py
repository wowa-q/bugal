# pylint: skip-file
# flake8: noqa
from datetime import date, datetime

import pathlib
import os
import shutil
from typing import Iterable

import pytest

from cfg import config
from libs import exceptions as err

from bugal.app import csv_handler

from fixtures import basic
from fixtures import csv_fx


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

# @pytest.mark.skip()
@pytest.mark.parametrize("csv_type", [
    ('classic'),
    ('beta'),
    ('2024'),
    ('daily'),   
])
def test_init_csv_handler(fx_single_csv, csv_type):
    
    if csv_type == 'classic':        
        h = csv_handler.ClassicInputAdapter(fx_single_csv)       
        # assert h.input_type == cfg.TransactionListClassic, "input type"
    elif csv_type == 'beta':
        h = csv_handler.ModernInputAdapter(fx_single_csv)
    elif csv_type == '2024':
        h = csv_handler.ModernInput_2024Adapter(fx_single_csv)
    elif csv_type == 'daily':
        h = csv_handler.DailyCardAdapter(fx_single_csv)
    assert h is not None

    assert h.input is not None, "input path is not initialized"
    assert h.src_account is None, f"Source account not initialized: {h.src_account}"

# @pytest.mark.skip()
@pytest.mark.parametrize("csv_type", [
    ('classic'),
    # ('beta'),
    # ('2024'),
    # ('daily'),   
])
def test_get_meta_data(fx_single_csv, csv_type):
    if csv_type == 'classic':        
        h = csv_handler.ClassicInputAdapter(fx_single_csv)       
        # assert h.input_type == cfg.TransactionListClassic, "input type"
    elif csv_type == 'beta':
        h = csv_handler.ModernInputAdapter(fx_single_csv)
    elif csv_type == '2024':
        h = csv_handler.ModernInput_2024Adapter(fx_single_csv)
    elif csv_type == 'daily':
        h = csv_handler.DailyCardAdapter(fx_single_csv)
    assert h is not None
    meta = h.get_meta_data()
    assert isinstance(meta, dict)
    assert h.src_account is not None, f"Source account was not updated: {h.src_account}"

# @pytest.mark.skip()
def test_get_transaction_list(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None
    # line is a generator
    line = h.get_transactions_as_list(fx_single_csv, h.CSV_START_ROW)
    assert isinstance(line, Iterable), f"Transaction is not a Generator: {line}"
    ln_tr = line.__next__()
    assert isinstance(ln_tr, list), f"Transaction as a list"
    assert len(ln_tr) > 0, f"Transaction received as list: {ln_tr}"

# @pytest.mark.skip()
def test_get_transaction(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None

    transrow = h.get_transaction()
    assert transrow is not None, f"Transaction row not created: {transrow}"
    # assert isinstance(transrow, list)
    assert isinstance(transrow.__next__(), dict)

# @pytest.mark.skip()
def test_get_checksum(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None

    checksum = h.get_checksum(fx_single_csv)
    assert checksum is not None, f"Checksum not created: {checksum}"
    assert isinstance(checksum, str)

# @pytest.mark.skip()
def test_get_account_nr(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None
    transrow = h.read_lines(fx_single_csv)
    account = h.extract_account_or_card_number(transrow.__next__())
    assert account is not None
    assert isinstance(account, str)

# @pytest.mark.skip()
def test_get_tr_value(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None
    # transrow = h.get_transactions_as_list(fx_single_csv, h.CSV_START_ROW)
    transrow = h.get_transaction()
    value = h.get_tr_value(transrow.__next__())
    assert value is not None
    assert isinstance(value, float), f"Value not float type: {value}"

################################################################
#                        Test with concrete data                                
################################################################

@pytest.mark.skip()
def test_get_tr_date(fx_single_csv):
    h = csv_handler.ClassicInputAdapter(fx_single_csv)
    assert h is not None
    line = []  #TODO: fixture needs to be prepared
    h._get_tr_date(line)