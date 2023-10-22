# pylint: skip-file
# flake8: noqa
from datetime import datetime, date
import pathlib
import os

import pytest


from context import bugal

from bugal import cfg
from bugal import repo
from bugal import bugal_orm
from bugal import model

from fixtures import basic
from fixtures import orm_fx
from fixtures import sql_fx


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"


@pytest.mark.skip()
def test_init_repo(fx_single_csv, fx_transaction_example_classic):
    orm = bugal_orm.BugalOrm(FIXTURE_DIR, fx_single_csv, db_type='memory')
    with pytest.raises(cfg.DbConnectionFaild):        
        none_repo = repo.TransactionsRepo(None)
    o_repo = repo.TransactionsRepo(orm)
    assert o_repo is not None, "Repo couldn't be initialized"
    with pytest.raises(cfg.RepoUseageError):
        assert o_repo.find_checksum('')
    with pytest.raises(cfg.NoValidTransactionData):
        assert o_repo.push_transactions('')
    with pytest.raises(cfg.NoValidTransactionData):
        assert o_repo.push_transactions(fx_transaction_example_classic)