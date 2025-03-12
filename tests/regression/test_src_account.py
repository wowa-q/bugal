# pylint: skip-file
# flake8: noqa
from datetime import date, datetime
import pathlib

import pytest

from cfg import config
from libs import exceptions as err
from bugal.app import csv_handler, model

from fixtures import basic
from fixtures import csv_fx

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()
""" Problem description:
The import of the csv file itself works, but the transactions don't have the source account.
The csv has the src account in its meta (one csv in for one account)

"""
def test_l1():

    line = ["Kontonummer:",
            "DE90120300001001670080 / Girokonto"]
    expected = 'DE90120300001001670080'
    handler = csv_handler.InputMaster()
    account = handler.extract_account_or_card_number(line)
    assert account == expected, f"Account received: {account} but was expected {expected}"

def get_date_object(par):
    datum = datetime.today()
    return datum

start_row = 6

def test_l2(fx_single_csv):
    csv_file = fx_single_csv
    expected = 'DE12345300001019363165'
    handler = csv_handler.InputMaster()
    account = handler.get_meta_data(csv_file, start_row, get_date_object)
    assert account['account'] == expected, f"Account received: {account['account'] } but was expected {expected}"

def test_l3(fx_single_csv_new):
    csv_file = fx_single_csv_new
    expected = 'DE12345300001019363165'
    handler = csv_handler.ModernInput_2024Adapter(csv_file)
    account = handler.get_meta_data()
    assert account['account'] == expected, f"Account received: {account['account'] } but was expected {expected}"
    assert handler.src_account == expected, f"Account at Handler: {handler.src_account} but was expected {expected}"
    
def test_l4(fx_single_csv_new):
    csv_file = fx_single_csv_new
    expected = 'DE12345300001019363165'
    config_ = config.get_config()
    config_.import_path = csv_file
    stack = model.make_stack(config_)
    account = stack.import_meta
    assert account['account'] == expected, f"Account received: {account['account'] } but was expected {expected}"

def make_dict():
    temp_dict = config.META_TRANSACTION.copy()
    temp_dict['tdate'] = get_date_object(None)
    temp_dict['text'] = ''
    temp_dict['konto'] = ''
    temp_dict['status'] = ''
    temp_dict['debitor'] = ''
    temp_dict['verwendung'] = ''
    temp_dict['value'] = '100'
    temp_dict['debitor_id'] = ''
    temp_dict['mandats_ref'] = ''
    temp_dict['customer_ref'] = ''
    temp_dict['src_konto'] = 'ABCD'
    return temp_dict
    
def test_l5(fx_single_csv_2024):
    csv_file = fx_single_csv_2024
    expected = 'DE12345300001019363165'
    tdata = make_dict()
    config_ = config.get_config()
    config_.import_path = csv_file
    stack = model.make_stack(config_)
    account = stack.import_meta
    assert account['account'] == expected, f"Account received: {account['account'] } but was expected {expected}"
    titem = stack.create_transaction(tdata)
    # Fehler gefunden und gefixt!
    assert titem.src_konto == expected, f"Account in Stack: {titem.src_konto}, but expected: {expected}"
