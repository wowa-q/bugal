# pylint: skip-file
# flake8: noqa

from datetime import datetime

import pytest

from context import bugal

from bugal import csv_handler
from bugal import model
from bugal import handler
from bugal import repo
from bugal import cfg

def read_list(lst):
    for item in lst:
        yield item


@pytest.mark.skip()
def test_transaction_creation_classic(fx_single_csv):
    
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    
    stack_transaction = None
    csv_transaction = None


    # gen_transaction = csv_importer.get_transactions()
    # trns = next(gen_transaction)
    # assert trns == 2, f"csv handler return value: {trns}"
    for csv_output in csv_importer.get_transactions():
        assert len(csv_output[1]) < 0, f"{csv_output[1]}"
        if len(csv_output[1]) > 0:
            stack_transaction = stack.create_transaction(csv_output[1])
            csv_transaction = csv_output[1].copy()
    assert csv_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
    assert stack_transaction is not None, f"STACK: Transacton not created {csv_transaction}"
    assert stack.nr_transactions != 0, f"no transaction were created {csv_transaction}"
    assert stack.nr_transactions == 4, f"number of classic transaction is different than provided by csv"
    
@pytest.mark.skip()
def test_transaction_creation_beta(fx_single_csv_new):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    stack.input_type = cfg.TransactionListBeta
    csv_importer.input_type = cfg.TransactionListBeta

    for transaction in csv_importer.get_transactions():
        stack.create_transaction(transaction)
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 3, f"number of BETA transaction is different than provided by csv: {stack.transactions[0]}"

@pytest.mark.skip()
def test_transaction_creation_works_with_single_line(fx_single_csv_single_line):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv_single_line)
    stack.input_type = cfg.TransactionListBeta
    csv_importer.input_type = cfg.TransactionListBeta
    
    for transaction in csv_importer.get_transactions():
        stack.create_transaction(transaction)
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 1, f"number of BETA transaction is different than provided by csv: {stack.transactions[0]}"

@pytest.mark.skip()
def test_write_transactions_to_db(fx):
    '''
    0. preparation
    0.1 db with transactions and history
    0.2 csv with transactions
    
    1. read csv file
    2. create transactions
    3. create history
    4. read history from db
    5. check checksum not available
    6. write transactions
    7. write history
    '''
    
    assert True


@pytest.mark.skip()
def test_read_transactions_from_db(fx):
    assert True

@pytest.mark.skip()
def test_no_import_of_double_csv(fx_single_csv):
    csv_importer1 = handler.CSVImporter(fx_single_csv)
    csv_importer2 = handler.CSVImporter(fx_single_csv)
    csv_importer1.input_type = cfg.TransactionListClassic
    csv_importer2.input_type = cfg.TransactionListClassic
    test_transaction = []
    for transaction in csv_importer1.get_transactions():
        assert transaction is not None, f"transaction not received - None"
        assert isinstance(transaction, list), f"returned transaction is not a list"
        assert transaction != [], f"empty list received for imported transaction"
        if len(test_transaction) == 0:
            test_transaction = transaction.copy()
    assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
    for transaction in csv_importer2.get_transactions():
        assert transaction is None, f"transactions repeatedly imported"

@pytest.mark.skip
def test_print_transactions_from_db(fx_xls_file, fx_db_file):
    assert False, f"not implemented"