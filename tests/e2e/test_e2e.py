# pylint: skip-file
# flake8: noqa

from datetime import datetime
from dataclasses import fields
import pytest

from context import bugal

from bugal import csv_handler
from bugal import model
from bugal import handler
from bugal import repo
from bugal import cfg


# @pytest.mark.skip()
def test_transaction_creation_classic(fx_single_csv):
    
    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    
    stack_transaction = None
    csv_transaction = None
    csv_transactions = []
    for csv_output in csv_importer.get_transactions():
        for ctr, line in enumerate(csv_output):
            assert len(line) > 0, f"{line}"
            if len(line) > 0:
                stack_transaction = stack.create_transaction(line)
                csv_transaction = line.copy()
                csv_transactions.append(line)
            if ctr == 0:
                assert csv_transaction[1] == "24.01.2023", f"transaction hat falschen Wert {line[1]}"             

    assert csv_transaction[1] == "16.05.2023", f"transaction hat falschen Wert {line[1]}" 
    assert 'ROSSMANN' in csv_transaction[3], f"transaction hat falschen Wert {line[3]}" 
    assert stack_transaction is not None, f"STACK: Transacton not created {csv_transaction}"
    # ensure all transactions are different, otherwise model will not create redundant transactions
    assert stack.nr_transactions == 5, f"number of classic transaction {len(csv_transactions)} is different than provided by csv"
    for transaction in stack.transactions:        
        for field in fields(transaction):
            attribute_name = field.name
            attribute_value = getattr(transaction, attribute_name)
            print(f"{attribute_name}: {attribute_value}")
        assert transaction.text == 'Classic', f"{transaction.text}"

@pytest.mark.skip()
def test_transaction_creation_beta(fx_single_csv_new):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    stack.input_type = cfg.TransactionListBeta
    csv_importer.input_type = cfg.TransactionListBeta
    ctr = 0
    for csv_output in csv_importer.get_transactions():
        for ctr, line in enumerate(csv_output):
            stack.create_transaction(line)
            
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 3, f"number of BETA transaction is different than provided by csv: {ctr}"

@pytest.mark.skip()
def test_transaction_creation_works_with_single_line(fx_single_csv_single_line):
    stack=model.Stack()
    csv_importer = handler.CSVImporter(fx_single_csv_single_line)
    stack.input_type = cfg.TransactionListBeta
    csv_importer.input_type = cfg.TransactionListBeta
    
    for csv_output in csv_importer.get_transactions():
        for ctr, line in enumerate(csv_output):
            stack.create_transaction(line)
    assert stack.nr_transactions != 0, f"no transaction were created"
    assert stack.nr_transactions == 1, f"number of BETA transaction is different than provided by csv: {stack.transactions[0]}"

# @pytest.mark.skip()
def test_write_transactions_to_db():
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
    
    assert False, "Test not implemetned: test_write_transactions_to_db"


@pytest.mark.skip()
def test_read_transactions_from_db():
    assert False, "Test not implemetned: test_read_transactions_from_db"

@pytest.mark.skip()
def test_no_import_of_double_transactions(fx_single_csv, ):
    # Where to check douplicate? 
    # Better first to pull hashes from DB. More memory, but quicker.
    csv_importer1 = handler.CSVImporter(fx_single_csv)
    csv_importer2 = handler.CSVImporter(fx_single_csv)
    csv_importer1.input_type = cfg.TransactionListClassic
    csv_importer2.input_type = cfg.TransactionListClassic
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    rp = repo.FakeRepo() # Fake repo can have a fix hash lists
    test_transaction = []

    for csv_output in csv_importer1.get_transactions():
        for ctr, line in enumerate(csv_output):
            # assert line is not None, f"transaction not received - None"
            # assert line != [], f"empty list received for imported transaction"
            stack.create_transaction(line)
            # if len(test_transaction) == 0:
            #     test_transaction = line.copy()
    assert test_transaction[0] == "24.01.2023", f"transaction hat falschen Wert {test_transaction}" 
    for csv_output in csv_importer2.get_transactions():
        for ctr, line in enumerate(csv_output):
            stack.create_transaction(line)
            # assert line != [], f"empty list received for imported transaction"
            # assert line is None, f"transactions repeatedly imported"
    rp.find_csv_checksum()

# @pytest.mark.skip()
def test_no_import_of_double_csv(fx_single_csv, ):
    # Where to check douplicate? 
    # Better first to pull hashes from DB. More memory, but quicker.
    csv_importer1 = handler.CSVImporter(fx_single_csv)
    csv_importer2 = handler.CSVImporter(fx_single_csv)
    csv_importer1.input_type = cfg.TransactionListClassic
    csv_importer2.input_type = cfg.TransactionListClassic
    checks1 = csv_importer1.get_checksum(csv_importer1.csv_files[0])
    checks2 = csv_importer1.get_checksum(csv_importer2.csv_files[0])
    assert checks1 == checks2, f"calculated checksum for the ame file is different"
    rp = repo.FakeRepo() # Fake repo can have a fix hash lists
    rp.find_csv_checksum(checks1)
    # im model oder service umsetzen: wenn repo die checksumme bereits hat soll die 
    # transaction aus dem Stack gelöscht werden

@pytest.mark.skip
def test_print_transactions_from_db(fx_xls_file, fx_db_file):
    assert False, f"not implemented"