# pylint: skip-file
# flake8: noqa
"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
from datetime import datetime

# 3rd party
import pytest
# from openpyxl import Workbook

# user packages

from bugal.app import model
from cfg import config as cfg

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_transaction_example_classic():
    data = ["01.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    return data

@pytest.fixture
def fx_transactions_list_example_classic():
    transactions = []
    data = ["01.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["02.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["03.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["04.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["01.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    return transactions

@pytest.fixture
def fx_transaction_example_beta():
    #data = ["01.01.22", "01.01.22", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    
    data = ["19.10.23","19.10.23","Gebucht","Angelina Merkel","Angelina Merkel","","Ausgang","-40,00 €","","",""]
    return data

@pytest.fixture
def fx_transactions_list_example_beta():
    transactions = []
    data = ["01.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["02.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["03.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["04.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["01.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["01.01.2022", "01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    return transactions

@pytest.fixture
def fx_stack_example(fx_transactions_list_example_classic):
    stack = model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    return stack

@pytest.fixture
def fx_import_history():
    history = ["example.csv", "csv", "01234", "01.12.2023", "31.12.2023", "01.01.2023", "54A489AA87E4A03CF2F0D9F4422833B9"]
    return history

@pytest.fixture
def fx_csv_meta_dict():
    datum = '22.09.2023'
    meta = cfg.CSV_META.copy()
    meta['end_date'] = '22.09.2023' 
    meta['start_date'] = '21.09.2023'
    meta['account'] = 'DE123456789'
    meta['file_ext'] = 'csv'
    meta['file_name'] = 'fx_dict'

    return meta