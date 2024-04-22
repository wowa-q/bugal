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

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()


@pytest.fixture
def fx_test_beta_csv():
    csv_file = None
    return csv_file

@pytest.fixture
def fx_test_classic_csv():
    csv_file = None
    return csv_file

