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
from bugal import bugal_orm

from fixtures.model_fx import fx_transaction_example_classic

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_test_db():
    # file_name = 'fx_test_db'
    # full = file_name + '.db'
    # file_path = FIXTURE_DIR / full
    
    # orm_handler = bugal_orm.BugalOrm(FIXTURE_DIR, full, 'sqlite')
    # stack=model.Stack()
    # stack.input_type = cfg.TransactionListClassic
    
    # t1 = stack.create_transaction(fx_transaction_example_classic)
    
    # orm_handler.write_to_transactions(t1)
    # ctr = orm_handler.get_transaction_ctr()

    # yield full
    file_data = [FIXTURE_DIR, "fx_test_db"]
    file_name = file_data[1]+'.db'
    file_path = file_data[0] / file_name
    with open(file_path, "w") as f:
        pass

    yield file_data
    time.sleep(0.1)
    # try:
    #     file_path.unlink()
    # except FileNotFoundError:
    #     pass
    
    