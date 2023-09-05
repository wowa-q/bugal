# pylint: skip-file
# flake8: noqa

import pathlib
from datetime import datetime
from dataclasses import fields
import pytest

from context import bugal

from bugal import service
from bugal import bugal_orm
from bugal import model
from bugal import handler
from bugal import repo
from bugal import cfg

from fixtures import basic
from fixtures import orm_fx
from fixtures import e2e_fx

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

# @pytest.mark.skip()
def test_write_classic_transactions_to_db(fx_test_db, fx_single_csv):

    csv_importer = handler.CSVImporter(fx_single_csv)
    csv_importer.input_type = cfg.TransactionListClassic
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    stack.set_src_account('123456')
    orm_handler = bugal_orm.BugalOrm(fx_test_db[0], fx_test_db[1], 'sqlite')
    t_ctr_orm = 0
    history_data = csv_importer.get_meta_data()
    stack_history = stack.create_history(history_data[0])
    for ctr, transactions in enumerate(csv_importer.get_transactions()):
        for ctr_t, transaction_c in enumerate(transactions, 1):
            assert len(transaction_c) > 0, f"the line is empty {transaction_c}"
            transaction_m = stack.create_transaction(transaction_c)
            orm_handler.write_to_transactions(transaction_m)
    assert ctr_t == 5, f"not all transactions generated {ctr_t}"
    t_ctr_orm = orm_handler.get_transaction_ctr()
    assert t_ctr_orm == 5, f"no transaction pushed {t_ctr_orm}"
    
    assert stack_history is not None, f"No history created"
    assert isinstance(stack_history, model.History), f""
    result =  orm_handler.write_to_history(stack_history)
    h_ctr_orm = orm_handler.get_history_ctr()
    assert result, f"pushing history to the DB failed"
    assert h_ctr_orm == 1, f"the history counter was not increased"
    src_account = stack_history.account
    datum = datetime(2023, 1, 23)
    filter = {'date-after': datum}
    rows = orm_handler.read_transactions(filter)
    assert len(rows) == 2, f"number of transactionrows isnot as expected"
    datum_list = []
    value_list = []
    account_list = []
    for row in rows:
        datum_list.append(row.datum)
        value_list.append(row.value)
        account_list.append(row.src_konto)
    assert '-51,00' in value_list, f"value not in the list" # \x80 ist Unicode-Zeichen für Euro
    assert account_list[0] == src_account, f"false account pulled from DB"

# @pytest.mark.skip()
def test_write_beta_transactions_to_db(fx_test_db, fx_single_csv_new):
    '''
    0. preparation
    0.1 new db 
    0.2 csv with transactions
    
    1. read csv file
    2. create csv transactions
    3. create stack transactions
    4. push stack transactions
    5. check number of transactions the same as in csv
    6. create history
    7. push the history to db
    8. check the number of history entries
    9. try to push the history again
    10. check the number of history entries
    11. check transaction table contant
    12. check history table contant
    '''
    csv_importer = handler.CSVImporter(fx_single_csv_new)
    csv_importer.input_type = cfg.TransactionListBeta
    stack=model.Stack()
    stack.input_type = cfg.TransactionListBeta
    orm_handler = bugal_orm.BugalOrm(fx_test_db[0], fx_test_db[1], 'sqlite')
    t_ctr_orm = 0
    history_data = csv_importer.get_meta_data()
    stack_history = stack.create_history(history_data[0])
    src_account = stack_history.account
    
    for ctr, transactions in enumerate(csv_importer.get_transactions()):
        for ctr_t, transaction_c in enumerate(transactions, 1):
            assert len(transaction_c) > 0, f"the line is empty {transaction_c}"
            transaction_m = stack.create_transaction(transaction_c)
            assert transaction_m.src_konto == src_account, f"transaction false"
            orm_handler.write_to_transactions(transaction_m)
    assert ctr_t == 3, f"not all transactions generated {ctr_t}"
    t_ctr_orm = orm_handler.get_transaction_ctr()
    assert t_ctr_orm == 3, f"no transaction pushed {t_ctr_orm}"
    
    
    assert stack_history is not None, f"No history created"
    assert isinstance(stack_history, model.History), f""
    result =  orm_handler.write_to_history(stack_history)
    h_ctr_orm = orm_handler.get_history_ctr()
    assert result, f"pushing history to the DB failed"
    assert h_ctr_orm == 1, f"the history counter was not increased"
    """
    Buchungsdatum [24.01.2022, 24.02.2022, 24.03.2022]
    value 54,97, 54,97, -42,60
    """
    datum = datetime(2022, 1, 23)
    filter = {'date-after': datum}
    rows = orm_handler.read_transactions(filter)
    assert len(rows) == 3, f"number of transactionrows isnot as expected"
    datum_list = []
    value_list = []
    account_list = []
    for row in rows:
        datum_list.append(row.datum)
        value_list.append(row.value)
        account_list.append(row.src_konto)

    assert '54,97 \x80' in value_list, f"value not in the list" # \x80 ist Unicode-Zeichen für Euro
    assert account_list[0] == src_account, f"false account pulled from DB"

# @pytest.mark.skip()
def test_CmdImportNewCsv(fx_test_db, fx_single_csv_new):
    handler_r = handler.CSVImporter(fx_single_csv_new)
    stack=model.Stack()
    handler_r.input_type = cfg.TransactionListBeta
    stack.input_type = cfg.TransactionListBeta
    repo = bugal_orm.BugalOrm(fx_test_db[0], fx_test_db[1], 'sqlite')

    cmd = service.CmdImportNewCsv(repo, stack, handler_r)
    result = cmd.execute()

    assert result > 0, f"No transactions imported {result}"

    # assert False, "Test not implemetned: test_CmdImportNewCsv"
