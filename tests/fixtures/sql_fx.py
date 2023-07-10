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
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_new_betaTransaction():
    data = ["2022-01-01", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    stack = model.Stack()
    stack.input_type = cfg.TransactionListBeta
    transaction = stack.create_transaction(data)
    
    return transaction

@pytest.fixture
def fx_new_classicTransactions_banch():
    
    t1 = model.Transaction("2022-01-01", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t2 = model.Transaction("2022-01-03", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t3 = model.Transaction("2022-01-02", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")

    return [t1, t2, t3]