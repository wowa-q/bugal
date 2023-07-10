# pylint: skip-file
# flake8: noqa
from datetime import date
import pathlib
import os

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

#@pytest.mark.skip()
def test_creagte_new_db(fx_new_db_flie_name, fx_new_betaTransaction):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    orm_handler.write_to_transactions(fx_new_betaTransaction)

    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)

    assert before < after, "no new db was created" 

# @pytest.mark.skip()
def test_create_banch_of_transactions(fx_new_db_flie_name, fx_new_classicTransactions_banch):
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, fx_new_db_flie_name, 'sqlite')
    orm_handler.write_many_to_transactions(fx_new_classicTransactions_banch)

    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)

    assert before < after, "no new db was created"
    # Data of the tables is not tested - no error is enough for the moment
    # TODO: add more tests of the data

# #@pytest.mark.skip()
# def test_load_transactions(fx_test_db_new):
#     engine = create_engine('sqlite:///' + str(fx_test_db_new), echo=True)
#     session = sessionmaker(engine)
#     repo = re.SqlAlchemyRepository(session)
#     assert repo is not None
#     repo.set_transaction()
#     repo.set_history()
#     repo.set_mapping()

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