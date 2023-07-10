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


FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_new_db_flie_name():
    file_name = FIXTURE_DIR / 'new_db.db'
    yield file_name
    try:
        file_name.unlink()
    except FileNotFoundError:
        pass 
