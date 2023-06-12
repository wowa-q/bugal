# pylint: skip-file
# flake8: noqa

from datetime import date

import pytest

from context import bugal

from bugal import model
from bugal import handler
from bugal import repo
from bugal import cfg

# @pytest.mark.skip()
def test_transaction_creation_classic(fx_single_csv):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv)
    stack.input_type = cfg.TransactionListClassic
    csv_importer.input_type = cfg.TransactionListClassic

    for transaction in csv_importer.get_transactions():
        stack.create_transaction(transaction)
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 4, f"number of classic transaction is different than provided by csv"

# @pytest.mark.skip()
def test_transaction_creation_beta(fx_single_csv_new):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    stack.input_type = cfg.TransactionListBeta
    csv_importer.input_type = cfg.TransactionListBeta

    for transaction in csv_importer.get_transactions():
        stack.create_transaction(transaction)
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 3, f"number of BETA transaction is different than provided by csv: {stack.transactions[0]}"

# @pytest.mark.skip()
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