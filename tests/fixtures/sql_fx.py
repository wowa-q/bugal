# pylint: skip-file
# flake8: noqa

"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
from datetime import datetime
import sqlite3
from sqlalchemy import create_engine

# 3rd party
import pytest
# from openpyxl import Workbook

# user packages
from context import bugal
from bugal import model
from bugal import cfg


FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_new_db_file_name():
    name = 'fx_new_db_created'
    file_path = pathlib.Path(FIXTURE_DIR / (name + '.db'))
    yield file_path
    time.sleep(0.1)
    try:
        file_path.unlink()
    except FileNotFoundError as e:
        print(f"Error deleting file: {e}") 

@pytest.fixture
def fx_new_betaTransaction():
    data = ["01.01.2022", "0.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    stack = model.Stack(cfg.TransactionListBeta)    
    transaction = stack.create_transaction(data)    
    return transaction

@pytest.fixture
def fx_new_classicTransactions_banch():
    stack = model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    t1 = stack.create_transaction(["01.01.2022", "01.01.2022", "text", "status", "debitor", "verwendung", "konto", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"])
    t2 = stack.create_transaction(["01.03.2022", "01.03.2022", "text", "status", "debitor", "verwendung", "konto", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"])
    t3 = stack.create_transaction(["01.04.2022", "01.04.2022", "text", "status", "debitor", "verwendung", "konto", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"])

    return [t1, t2, t3]

@pytest.fixture
def fx_history(fx_checksum_repo_exist):
    stack = model.Stack(cfg.TransactionListClassic)
    meta = cfg.CSV_META.copy()
    meta['file_name'] = 'auszug1'
    meta['file_ext'] = 'csv'
    meta['checksum'] = fx_checksum_repo_exist
    meta['account'] = 'account'
    meta['start_date'] = datetime.strptime('31.12.2023', "%d.%m.%Y")
    meta['end_date'] = datetime.strptime('31.12.2023', "%d.%m.%Y")
    h1 = stack.create_history(meta)

    return h1

@pytest.fixture
def fx_history_unique():
    hash_v = random.randint(100000, 999999)
    data_list = [
    "file_name_value",
    "file_type_value",
    "account_value",
    "2022.02.20",
    "2022.02.20",
    "2022.02.02",
    hash_v
    ]
    stack = model.Stack(cfg.TransactionListClassic)
    dc = cfg.CSV_META.copy()
    dc['file_name'] = 'auszug1'
    dc['file_ext'] = 'csv'
    dc['checksum'] = hash_v
    dc['account'] = 'DE123'
    dc['start_date'] = "31.12.2023"
    dc['end_date'] = "01.12.2023"
    history = stack.create_history(dc)
    if not isinstance(history, model.History):
        raise ValueError("Not History Type was returned")
    # history = model.History(*data_list)
    return history

@pytest.fixture
def fx_transaction_unique():
    data = ["01.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", str(random.randint(100000, 999999)), str(random.randint(100000, 999999)), "mandats_ref", "customer_ref", "src_konto"]
    stack = model.Stack(cfg.TransactionListClassic)
    transaction = stack.create_transaction(data)

    return transaction

@pytest.fixture
def fx_checksum_repo_exist():
    checksum = '123456789'
    return checksum

@pytest.fixture
def fx_checksum_repo_not_exist():
    checksum = '12345678910'
    return checksum
