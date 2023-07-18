# pylint: skip-file
# flake8: noqa

"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
from datetime import datetime
import sqlite3 as sql

# 3rd party
import pytest
# from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, clear_mappers

# user packages
from context import bugal
from bugal import model
from bugal import cfg
from bugal import orm

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_test_db_new():
    """Definitiaon of DB file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    db_file = FIXTURE_DIR / "test_db_created.db"
    conn = sql.connect(db_file)
    cursor = conn.cursor()
    # 
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees
                (Emp_ID INT, Name TEXT, Position TEXT);''')
    conn.commit()
    conn.close()

    yield db_file
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        db_file.unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def fx_db_orm_engine(fx_test_db_new):
    engine = create_engine(f'sqlite:///{fx_test_db_new}')
    return engine

@pytest.fixture
def in_memory_db_engine():
    engine = create_engine("sqlite:///:memory:")
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    orm.start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()