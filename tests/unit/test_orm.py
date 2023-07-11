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
from bugal import repo as re
from bugal import bugal_orm
from bugal import model

from fixtures import basic
from fixtures import orm_fx
from fixtures import sql_fx


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

@pytest.mark.skip()
def test_creagte_new_db(fx_new_db_flie_name, fx_new_betaTransaction):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    orm_handler.write_to_transactions(fx_new_betaTransaction)
    orm_handler.close_connection()

    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)

    assert before < after, "no new db was created" 

@pytest.mark.skip()
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

@pytest.mark.skip()
def test_read_transactions(fx_new_db_flie_name, fx_new_classicTransactions_banch):
    
    # orm_handler = bugal_orm.BugalOrm('memory')
    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
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


#@pytest.mark.skip()
# def test_load_history(session):
#     session.execute(
#     "INSERT INTO history (file_name, file_type, account, min_date, max_date, import_date, checksum) VALUES "
#     "('csv1', 'csv', 12, '12.01.2021', '15.01.2021', '16.01.2021', 12345), "
#     "('csv2', 'csv', 12, '12.01.2021', '15.01.2021', '16.01.2021', 12346)"
#     )

#     expected = [
#         model.History('csv1', 'csv', 12, '12.01.2021', '15.01.2021', '16.01.2021', 12345),
#         model.History('csv2', 'csv', 12, '12.01.2021', '15.01.2021', '16.01.2021', 12346),

#     ]
#     assert session.query(model.OrderLine).all() == expected




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