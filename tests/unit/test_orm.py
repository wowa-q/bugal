# pylint: skip-file
# flake8: noqa
from datetime import date
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

# @pytest.mark.skip()
def test_creagte_new_transaction(fx_new_db_flie_name, fx_new_betaTransaction):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)
    assert before < after, "no new db was created"
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
def test_create_banch_of_transactions(fx_new_db_flie_name, fx_new_classicTransactions_banch):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)
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
def test_read_transactions(fx_new_db_flie_name, fx_new_classicTransactions_banch):
    
    # orm_handler = bugal_orm.BugalOrm('memory')
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    
    checksums = []
    for transaction in fx_new_classicTransactions_banch:
        checksums.append(hash(transaction))
    assert len(checksums) == 3, f"{checksums}"
    assert len(set(checksums)) == 3, f"{set(checksums)} "
    
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)
    filter = {'datum': '2022-01-01'}
    transactions = orm_handler.read_transactions(filter)
    
    orm_handler.close_connection()
    
    assert len(transactions) == 3, "no transactions returned"
    assert transactions[0].datum == '2022-01-01', f"transaction: {transactions}"
    
# @pytest.mark.skip()
def test_creagte_new_history(fx_new_db_flie_name, fx_history):
    
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    orm_handler.write_to_history(fx_history)
    orm_handler.close_connection()
    
    columns = orm_handler.inspector.get_columns('history')
    assert len(columns) == 8, f"history table must have 8 columns {columns} are present"

def make_History_entry(db_path, entry=[]):
    default = ['file name default',
               'file type default',
               'account default',
               'min date default',
               'max date default',
               'import date default',
               'checksum default']
    columns = []
    if len(entry) > 0:
        columns = entry.copy()
    else:
        columns = default.copy()
    # Vorbereitung der DB
    conn = sqlite3.connect(db_path)    
    # Datenbankcursor erstellen
    cursor = conn.cursor()
    # vorher prüfen ob die Tabelle bereits existiert
    cursor.execute('''PRAGMA table_info("History")''')
    if len(cursor.fetchall()) == 0:
        # Tabelle erstellen
        cursor.execute('''
                CREATE TABLE History (
                    id INTEGER PRIMARY KEY,
                    file_name TEXT,
                    file_type TEXT,
                    account TEXT,
                    min_date TEXT,
                    max_date TEXT,
                    import_date TEXT,
                    checksum TEXT
                )
            ''')
        
    # Beispiel-INSERT-Abfrage mit 9 Bindungen
    cursor.execute("INSERT INTO History (file_name, file_type, account, min_date, max_date, import_date, checksum) VALUES (?, ?, ?, ?, ?, ?, ?)", (columns[0], columns[1], columns[2], columns[3], columns[4], columns[5], columns[6]))
    # Änderungen in die Datenbank übernehmen
    conn.commit()
    # Datenbankverbindung schließen
    conn.close()

# @pytest.mark.skip()
def test_repo_find_checksum(fx_new_db_flie_name, fx_checksum_repo_exist, fx_checksum_repo_not_exist):
    db_path = FIXTURE_DIR / 'test_db.db'
    row = ['file name',
               'file type',
               'account',
               'min date',
               'max date',
               'import date',
               fx_checksum_repo_exist]
    make_History_entry(db_path, entry=row)
    make_History_entry(fx_new_db_flie_name)
    
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, 'test_db', 'sqlite')
    result_exist = orm_handler.find_csv_checksum(fx_checksum_repo_exist)
    result_not_exist = orm_handler.find_csv_checksum(fx_checksum_repo_not_exist)
    orm_handler.close_connection()
    assert result_exist == True, f"Checksum not found in the History table {result_exist}"
    assert result_not_exist == False, f"Checksum found in the History table {result_not_exist}"

    orm_handler = bugal_orm.BugalOrm(pth=fx_new_db_flie_name, db_type='sqlite')
    result_exist = orm_handler.find_csv_checksum(fx_checksum_repo_exist)
    result_not_exist = orm_handler.find_csv_checksum(fx_checksum_repo_not_exist)
    orm_handler.close_connection()
    assert result_exist == True, f"Checksum not found in the History table {result_exist}"
    assert result_not_exist == False, f"Checksum found in the History table {result_not_exist}"
    try:
        db_path.unlink()
    except FileNotFoundError:
        pass

# @pytest.mark.skip()
def test_repo_push_history(fx_new_db_flie_name, fx_history_unique):
    # model create history

    # repo push new history into DB
    # DB (SQL) checks if the hash exists
    # if repo couldn't push - checksum exists and csv will not be imported
    # error message will be returned: "csv was already imported"
    
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')            
    # orm_handler = bugal_orm.BugalOrm(pth=fx_new_db_flie, db_type='sqlite')
    # assert pathlib.Path(fx_new_db_flie).is_file(), f"No db file created"
    # assert fx_new_db_flie.exists(), f"No db file created 2"
    result_not_exist = orm_handler.write_to_history(fx_history_unique)
    assert result_not_exist == True, f"History couldn't be written"
    result_not_exist = orm_handler.find_csv_checksum(fx_history_unique.checksum)
    assert result_not_exist == True, f"Checksum found in the History table {result_not_exist}"
    
    result_exist = orm_handler.write_to_history(fx_history_unique)
    assert result_exist == False, f"History was written again"
    
    
    orm_handler.close_connection()
    
    
    assert True, f"Not implemented"

@pytest.mark.skip()
def test_repo_push_transaction(fx_new_db_flie_name, fx_transaction_unique):
    # model create history

    # repo push new history into DB
    # DB (SQL) checks if the hash exists
    # if repo couldn't push - checksum exists and csv will not be imported
    # error message will be returned: "csv was already imported"
    
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')            
    result_not_exist = orm_handler.write_to_transactions(fx_transaction_unique)
    assert result_not_exist == True, f"History couldn't be written"
    result_not_exist = orm_handler.find_transaction_checksum(fx_transaction_unique.checksum)
    assert result_not_exist == True, f"Checksum found in the History table {result_not_exist}"
    
    result_exist = orm_handler.write_to_history(fx_transaction_unique)
    assert result_exist == False, f"History was written again"
    
    
    orm_handler.close_connection()
    
    
    assert True, f"Not implemented"


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