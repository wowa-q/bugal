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

def get_csv_from_templates(type):
    if type == 'classic':
        file_name = 'classic.test'
        file_name_new = 'classic.csv'
    else:
        file_name = 'beta.test'
        file_name_new = 'beta.csv'
    original = FIXTURE_DIR / file_name
    new = FIXTURE_DIR / file_name_new
    with open(original, 'r', encoding='ISO-8859-1') as original_file, \
     open(new, 'w', encoding='ISO-8859-1') as new_file:
        # Lesen Sie den Inhalt der Originaldatei
        inhalt = original_file.read()
        # Schreiben Sie den Inhalt in die neue Datei
        new_file.write(inhalt)
    new_file1 = new
    if type == 'classic':
        file_name = 'classic2.test'
        file_name_new = 'classic2.csv'
    else:
        file_name = 'beta2.test'
        file_name_new = 'beta2.csv'
    original = FIXTURE_DIR / file_name
    new = FIXTURE_DIR / file_name_new
    with open(original, 'r', encoding='ISO-8859-1') as original_file, \
     open(new, 'w', encoding='ISO-8859-1') as new_file:
        # Lesen Sie den Inhalt der Originaldatei
        inhalt = original_file.read()
        # Schreiben Sie den Inhalt in die neue Datei
        new_file.write(inhalt)
    new_file2 = new
    return (new_file1, new_file2)


@pytest.fixture
def fx_test_db():
    file_data = [FIXTURE_DIR, "fx_test_db"]
    file_name = file_data[1]+'.db'
    file_path = file_data[0] / file_name

    yield file_path
    time.sleep(0.1)
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass
    
@pytest.fixture
def fx_test_classic_csv():
    csv_file1, csv_file2 = get_csv_from_templates('classic')
    
    yield csv_file1, csv_file2
    time.sleep(0.1)
    try:
        csv_file1.unlink()
        csv_file2.unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def fx_test_beta_csv():
    csv_file1, csv_file2 = get_csv_from_templates('beta')

    yield csv_file1, csv_file2
    time.sleep(0.1)
    try:
        csv_file1.unlink()
        csv_file2.unlink()
    except FileNotFoundError:
        pass