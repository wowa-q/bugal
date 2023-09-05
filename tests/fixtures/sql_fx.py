# pylint: skip-file
# flake8: noqa

"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
from datetime import datetime
import sqlite3

# 3rd party
import pytest
# from openpyxl import Workbook

# user packages
from context import bugal
from bugal import model
from bugal import cfg


FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_new_db_flie_name():
    file_name = 'fx_new_db_created'
    full = file_name + '.db'
    file_path = FIXTURE_DIR / full
    yield file_name
    time.sleep(0.1)
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def fx_new_db_flie():
    full = 'fx_new_db_created' + '.db'
    file_path = FIXTURE_DIR / full
    yield file_path
    time.sleep(0.1)
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_new_betaTransaction():
    data = ["01.01.2022", "0.01.2022", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    stack = model.Stack()
    stack.input_type = cfg.TransactionListBeta
    transaction = stack.create_transaction(data)
    
    return transaction

@pytest.fixture
def fx_new_classicTransactions_banch():
    
    t1 = model.Transaction("01.01.2022", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t2 = model.Transaction("03.01.2022", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t3 = model.Transaction("04.01.2022", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")

    return [t1, t2, t3]

@pytest.fixture
def fx_history():
    
    h1 = model.History("auszug1", "csv", "DE123", "31.12.2023", "03.01.2022", "01.01.2022", "super checksum")

    return h1

@pytest.fixture
def fx_history_unique():
    hash_v = random.randint(100000, 999999)
    data_list = [
    "file_name_value",
    "file_type_value",
    "account_value",
    "import_date_value",
    "max_date_value",
    "min_date_value",
    hash_v
    ]

    history = model.History(*data_list)
    return history

@pytest.fixture
def fx_transaction_unique():
    
    data = ["2022.01.01", "STATUS", "sender", "receiver", "verwendung", "typ", random.randint(100000, 999999), str(random.randint(100000, 999999)), "mandats_ref", "customer_ref", "src_konto"]
    t3 = model.Transaction("2022.01-02", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")

    transaction = model.Transaction(*data)
    return transaction

@pytest.fixture
def fx_checksum_repo_exist():
    checksum = '123456789'
    return checksum

@pytest.fixture
def fx_checksum_repo_not_exist():
    checksum = '12345678910'
    return checksum
