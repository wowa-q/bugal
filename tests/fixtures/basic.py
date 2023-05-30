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
def fx_mandatory_sheets():
    return ['Regeln',
            'Historie', 
            'Properties',
            'Transaktionen',
            'Jahr',
            'Guide',
            ]

@pytest.fixture
def fx_xls_file():
    xsl_file = FIXTURE_DIR / 'test.xlsx'
    yield xsl_file 
    # delete file after test
    try:
        xsl_file.unlink()
    except FileNotFoundError:
        pass
    except PermissionError:
        time.sleep(5)
        xsl_file.unlink()

@pytest.fixture
def fx_transaction_example():
    data = ["2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
    return data

@pytest.fixture
def fx_transactions_list_example():
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
def fx_stack_example(fx_transactions_list_example):
    stack = model.Stack()
    for line in fx_transactions_list_example:
        stack.create_transaction(line)
    return stack

@pytest.fixture
def fx_export_filter_aggregate():
    fil = None
    return fil

@pytest.fixture
def fx_export_filter_aggregate():
    fil = None
    return fil

@pytest.fixture
def fx_xls_file2create():
    """Definitiaon of excel file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    xls_file = FIXTURE_DIR / "test_haushalt.xlsx"
    yield xls_file
    # delete the modified db file and copy one to make repeat of the test possible
    # try:
    #     xls_file.unlink()
    # except FileNotFoundError:
    #     pass

@pytest.fixture
def fx_month_data():
    month_data = []
    month_data_header = [
        'id',
        'date',
        'booking-date',
        'text',
        'debitor',
        'verwendung',
        'konto',
        'blz',
        'value',
        'debitor-id',
        'mandat',
        'customer',
        'class',
        'category'
    ]
    month_data_row = []

    month_data.append(month_data_header)
    # for i in range(10):
    #     for i in range(1, 14):
    #         month_data_row.append(random.randint(1, 100))
    #     month_data.append(month_data_row)
    return month_data_header

# @pytest.fixture
# def fx_xls_template(fx_xls_file2create):
#     wb = Workbook(write_only=True)
#     ws = wb.create_sheet()
#     ws.title='Jan'
#     for irow in range(10):
#         ws.append(['%d' % i for i in range(12)])
#     wb.save(fx_xls_file2create)
