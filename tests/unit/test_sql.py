# pylint: skip-file
# flake8: noqa

import os
import pathlib
import pytest

from context import bugal

from bugal import cfg
from bugal import repo

FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"


@pytest.mark.skip()
def test_sql_db_created(fx_new_db_flie_name):
    fx_new_db_flie_name 
    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    before = len(fileList)

    sql_repo = repo.SqlRepo('sqlite')
    sql_repo.create_new_db(FIXTURE_DIR, 'new_db')

    fileList=list(FIXTURE_DIR.glob('**/*.db'))
    after = len(fileList)

    assert before < after, "no new db was created"
    
