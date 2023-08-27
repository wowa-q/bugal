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
from bugal import bugal_orm

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

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

@pytest.fixture
def fx_in_memory_db():
    dugal_db = bugal_orm.BugalOrm('memory')
    
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()