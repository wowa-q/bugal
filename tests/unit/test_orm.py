# pylint: skip-file
# flake8: noqa
from datetime import datetime, date
import pathlib
import os
import time
import pytest
from openpyxl import load_workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sqlite3

from context import bugal

from bugal import cfg
from bugal import repo
from bugal import bugal_orm
from bugal import model

from fixtures import basic
from fixtures import orm_fx
from fixtures import sql_fx


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

#@pytest.mark.skip()
def test_creagte_new_transaction(fx_new_db_file_name, fx_new_betaTransaction):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)
    assert before < after, f"no new db was created {fx_new_db_file_name}"
    # test write transactions
    result_not_exist = orm_handler.write_to_transactions(fx_new_betaTransaction)
    assert result_not_exist == True, f"Transaction couldn't be written"
    # test search for transaction hash
    result_not_exist = orm_handler.find_transaction_checksum(hash(fx_new_betaTransaction))
    assert result_not_exist == True, f"Checksum not found in the Transactions table {hash(fx_new_betaTransaction)}"
    # test try to write the same transaction again
    result_exist = orm_handler.write_to_transactions(fx_new_betaTransaction)
    assert result_exist == False, f"Transaction {fx_new_betaTransaction} was written again"
    orm_handler.close_connection()

# @pytest.mark.skip()
def test_create_banch_of_transactions(fx_new_db_file_name, fx_new_classicTransactions_banch):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)
    assert isinstance(fx_new_classicTransactions_banch[0].date, date), f"Transaction Datum is nicht vom Typ date: {fx_new_classicTransactions_banch[0].date}"
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)
    ctr = orm_handler.get_transaction_ctr()
    assert ctr ==  3, f"Transaction counter {ctr} wrong"
    orm_handler.close_connection()

    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)

    assert before < after, "no new db was created"
    # Data of the tables is not tested - no error is enough for the moment
    # TODO: add more tests of the data
    tables = [
        'transactions', 'history', 'eigenschaften', 'mapping', #'rules'
    ]
    for table in tables:
        assert orm_handler.inspector.has_table(table), f"Table: {table} doesn't exist"

# @pytest.mark.skip()
def test_create_banch_of_transactions_with_duplicate(fx_new_db_file_name, fx_new_classicTransactions_banch):
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    fx_new_classicTransactions_banch.append(fx_new_classicTransactions_banch[0])
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)
    ctr = orm_handler.get_transaction_ctr()
    assert len(fx_new_classicTransactions_banch) > 3, f"List was not enhanced"
    assert ctr ==  3, f"duplicate transaction imported {ctr}"

# @pytest.mark.skip()
def test_read_transactions(fx_new_db_file_name, fx_new_classicTransactions_banch):
    
    # orm_handler = bugal_orm.BugalOrm('memory')
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    
    checksums = []
    for transaction in fx_new_classicTransactions_banch:
        checksums.append(hash(transaction))
    assert len(checksums) == 3, f"{checksums}"
    assert len(set(checksums)) == 3, f"{set(checksums)} "
    
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)
    filter = {'date-after': '01.01.2021'}
    transactions = orm_handler.read_transactions(filter)
    
    orm_handler.close_connection()
    
    assert len(transactions) == 3, "no transactions returned"
    datum = datetime.strptime('01.01.2022', '%d.%m.%Y').date()
    assert transactions[0].datum == datum, f"transaction: {transactions}"
    
# @pytest.mark.skip()
def test_creagte_new_history(fx_new_db_file_name, fx_history):
    assert isinstance(fx_history, model.History), f"th fixture is not History instance"
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    orm_handler.write_to_history(fx_history)
    orm_handler.close_connection()
    
    columns = orm_handler.inspector.get_columns('history')
    assert len(columns) == 8, f"history table must have 8 columns {columns} are present"

# @pytest.mark.skip()
def test_repo_find_checksum(fx_new_db_file_name, fx_history, fx_checksum_repo_exist, fx_checksum_repo_not_exist):
    
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')
    orm_handler.write_to_history(fx_history)
    result_exist = orm_handler.find_csv_checksum(fx_checksum_repo_exist)
    result_not_exist = orm_handler.find_csv_checksum(fx_checksum_repo_not_exist)
    orm_handler.close_connection()
    assert result_exist == True, f"Checksum not found in the History table {result_exist}"
    assert result_not_exist == False, f"Checksum found in the History table {result_not_exist}"

# @pytest.mark.skip()
def test_repo_push_history(fx_new_db_file_name, fx_history_unique):
    # model create history
    # repo push new history into DB
    # DB (SQL) checks if the hash exists
    # if repo couldn't push - checksum exists and csv will not be imported
    # error message will be returned: "csv was already imported"
    
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')            
    
    ctr1 = orm_handler.get_history_ctr()# orm_handler = bugal_orm.BugalOrm(pth=fx_new_db_file_name, db_type='sqlite')
    # assert pathlib.Path(fx_new_db_file_name).is_file(), f"No db file created"
    # assert fx_new_db_file_name.exists(), f"No db file created 2"
    assert isinstance(fx_history_unique, model.History), f"fixture is not History"
    result_not_exist = orm_handler.write_to_history(fx_history_unique)
    assert result_not_exist == True, f"History couldn't be written"
    ctr2 = orm_handler.get_history_ctr()

    result_not_exist = orm_handler.find_csv_checksum(fx_history_unique.checksum)
    assert result_not_exist == True, f"Checksum found in the History table {result_not_exist}"
    
    result_exist = orm_handler.write_to_history(fx_history_unique)
    assert result_exist == False, f"History was written again"
    assert ctr2 > ctr1, f"History counter wasn't increased"
    
    orm_handler.close_connection()
    
    
    assert True, f"Not implemented"

# @pytest.mark.skip()
def test_repo_push_transaction(fx_new_db_file_name, fx_transaction_unique):
    # model create history

    # repo push new history into DB
    # DB (SQL) checks if the hash exists
    # if repo couldn't push - checksum exists and csv will not be imported
    # error message will be returned: "csv was already imported"
    
    orm_handler = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite')          
    result_not_exist = orm_handler.write_to_transactions(fx_transaction_unique)
    assert result_not_exist == True, f"Transaction couldn't be written"
    result_not_exist = orm_handler.find_transaction_checksum(hash(fx_transaction_unique))
    assert result_not_exist == True, f"Checksum found in the Transactions table {result_not_exist}"
    ctr_before = orm_handler.get_transaction_ctr()
    result_exist = orm_handler.write_to_transactions(fx_transaction_unique)
    assert result_exist == False, f"Transaction was written again"
    ctr_after = orm_handler.get_transaction_ctr()
    assert ctr_after == ctr_before, f"New transaction pushed to DB, before: {ctr_before} and after: {ctr_after}"
    
    with pytest.raises(ValueError):
        orm_handler.write_to_transactions('fx_transaction_unique')

    orm_handler.close_connection()
    ctr_t1 = orm_handler.get_transaction_ctr()
    orm_handler2 = bugal_orm.BugalOrm(fx_new_db_file_name, 'sqlite') 
    ctr_t2 = orm_handler2.get_transaction_ctr()
    assert ctr_t2 == ctr_t1, f"Not the same number of transactions"

@pytest.mark.skip()
def test_init_bugal_orm(fx_new_db_file_name):
    with pytest.raises(FileNotFoundError):
        orm = bugal_orm.BugalOrm('FIXTURE_DIR')

    with pytest.raises(cfg.DbConnectionFaild):
        orm = bugal_orm.BugalOrm(FIXTURE_DIR, db_type='')
    
    orm = bugal_orm.BugalOrm(FIXTURE_DIR)
    assert orm is not None, f"undefined initialization"
    assert orm.engine is not None, f"orm engine was not created"
    db_file = FIXTURE_DIR / pathlib.Path('.db')
    try:
        db_file.unlink()
    except FileNotFoundError as e:
        print(f"Error deleting file: {e}")

    orm = bugal_orm.BugalOrm(FIXTURE_DIR, 'test')
    assert orm is not None, f"undefined initialization"
    assert orm.engine is not None, f"orm engine was not created"

    with open('test.db', 'w') as datei:
        datei.write('test')
    file_pth = FIXTURE_DIR / pathlib.Path('test.db')
    orm = bugal_orm.BugalOrm(file_pth)
    assert orm is not None, f"undefined initialization"
    assert orm.engine is not None, f"orm engine was not created"
    db_file = FIXTURE_DIR / pathlib.Path('test.db')
    try:
        db_file.unlink()
    except FileNotFoundError as e:
        print(f"Error deleting file: {e}")
    # NOT SUPPORTED
    # orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_file_name, 'sqlite')
    # assert orm_handler is not None, "bugal_orm couldn not be correctly initialized"
    # assert orm_handler.engine is not None, f"orm engine was not created"
    # db_file = FIXTURE_DIR / pathlib.Path(fx_new_db_file_name + '.db')
    # try:
    #     db_file.unlink()
    # except FileNotFoundError as e:
    #     print(f"Error deleting file: {e}")
    
    # orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_file_name, 'memory')
    # assert orm_handler is not None, "bugal_orm couldn not be correctly initialized"
    # assert orm_handler.engine is not None, f"orm engine was not created"

    orm_handler = bugal_orm.BugalOrm(db_type='memory')
    assert orm_handler is not None, "bugal_orm couldn not be correctly initialized"
    assert orm_handler.engine is not None, f"orm engine was not created"
'''
Tests to be executed:
    DB created
    Table creation
    connection
    commit 
    rollback

    query column x
    query transaction types
    ..
    insert new transaction
    insert new property
    insert new mapping
    insert new rule

'''    