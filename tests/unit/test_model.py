# pylint: skip-file
# flake8: noqa


from datetime import date, datetime
import pathlib
from time import sleep
import pytest
from types import SimpleNamespace

from bugal.app import csv_handler
from bugal.app import gen_handler 
from bugal.app.model import Stack
from bugal.app.model import Filter
from bugal.app import model
from cfg import config
from libs import exceptions as err


from fixtures import basic
from fixtures import csv_fx
from fixtures import model_fx
from fixtures import sql_fx


#TODO: gen_handler needs to be tested

# @pytest.mark.skip()
def test_validate_import_file(fx_classic_csv_config):
    result = model.validate_import_file(fx_classic_csv_config)
    assert result == True
    cfg_ = SimpleNamespace(import_type='CLASSIC',     
                           import_path='fx_classic_csv_config.import_path',
                           dbpath=fx_classic_csv_config.dbpath,
                           archive=fx_classic_csv_config.archive,
                           export_path=fx_classic_csv_config.export_path)
    with pytest.raises(err.NoCsvFilesFound):
        result = model.validate_import_file(cfg_)

# @pytest.mark.skip()    
def test_make_stack(fx_classic_csv_config):
    stack = model.make_stack(fx_classic_csv_config)
    assert stack is not None
    
    assert stack.import_meta is not None
    assert stack.import_adapter is not None
    checksum = stack.import_adapter.get_checksum(fx_classic_csv_config.import_path)
    assert checksum is not None
    cfg_ = SimpleNamespace(import_type='CLASSI',    # produce Typo 
                           import_path=fx_classic_csv_config.import_path,
                           dbpath=fx_classic_csv_config.dbpath,
                           archive=fx_classic_csv_config.archive,
                           export_path=fx_classic_csv_config.export_path)
    with pytest.raises(err.NoInputTypeSet):
        result = model.make_stack(cfg_)

#TODO: Erst repo testen
# @pytest.mark.skip()    
def test_compare_hash(fx_classic_csv_config, fx_new_db_file_name):
    stack = model.make_stack(fx_classic_csv_config)
    checksum = stack.import_adapter.get_checksum(fx_classic_csv_config.import_path)
    result = model.compare_hash(checksum, fx_new_db_file_name)
    assert result is None

# @pytest.mark.skip()
def test_csv_import(fx_classic_csv_config):
    with pytest.raises(err.ModelStackError):
        model.start_csv_import(fx_classic_csv_config, None)
    stack = Stack('')
    with pytest.raises(err.ModelStackError):
        model.start_csv_import(fx_classic_csv_config, stack)
    result = model.validate_import_file(fx_classic_csv_config)
    stack = model.make_stack(fx_classic_csv_config)
    ctr = model.start_csv_import(fx_classic_csv_config, stack)
    assert isinstance(ctr, int)
    assert ctr == 5, f"Counter for imported transactions: {ctr}"
    result = model.update_history(fx_classic_csv_config, stack)
    assert result == True, f"History not updated in repo: {result}"



################ not implemented ################

@pytest.mark.skip()
def test_store_transactions_in_db(fx_transactions_list_example_classic):
    stack=model.Stack('cfg.TransactionListClassic')

    assert len(stack.transactions) == 0

    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    stack.push_transactions('')
    # one transaction is double and will be removed from the list before push
    assert len(stack.transactions) == 4
    assert stack.filter.max_date == date.fromisoformat("2022-01-04")
    assert stack.filter.min_date == date.fromisoformat("2022-01-01")
    # TODO Test history automatically updated, when DB is changed


@pytest.mark.skip()
def test_store_import_history_in_db(fx_import_history):
    stack=model.Stack('cfg.TransactionListBeta')
    stack.update_history(fx_import_history)
    assert False, f"Not implemented"
    # meta = cfg.CSV_META.copy()


