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
def fx_transaction_example_classic():
    data = ["2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    return data

@pytest.fixture
def fx_transactions_list_example_classic():
    transactions = []
    data = ["2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-02", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-03", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-04", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    return transactions

@pytest.fixture
def fx_transaction_example_beta():
    data = ["2022-01-01", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    return data

@pytest.fixture
def fx_transactions_list_example_beta():
    transactions = []
    data = ["2022-01-01", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-02", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-03", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-04", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    data = ["2022-01-01", "2022-01-01", "STATUS", "sender", "receiver", "verwendung", "typ", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    transactions.append(data)
    return transactions

@pytest.fixture
def fx_stack_example(fx_transactions_list_example_classic):
    stack = model.Stack()
    stack.input_type = cfg.TransactionListClassic
    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    return stack

@pytest.fixture
def fx_import_history():
    history = ["example.csv", "csv", "01234", "2022-12-01", "2022-12-31", "2023-01-01", "54A489AA87E4A03CF2F0D9F4422833B9"]
    return history

