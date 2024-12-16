# pylint: skip-file
# flake8: noqa

import pathlib
from datetime import datetime
from dataclasses import fields
import pytest

from context import bugal

from bugal import service
from bugal.app import model
from bugal.app import handler
from bugal.db import repo
from bugal.cfg import cfg

from fixtures import basic
from fixtures import orm_fx
from fixtures import e2e_fx

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

# @pytest.mark.skip()
@pytest.mark.parametrize("csv_type, start, end, value, expected", [
    ('beta', '17.10.2023', '19.10.2023', -40, 5),  # 5 number of transactions
    ('alpha', '16.01.2023', '24.01.2023', -51, 5),   # 5 number of transactions
])
def test_CmdImportCsv_via_repo(csv_type, 
                               start, 
                               end, 
                               value, 
                               expected, 
                               fx_test_beta_csv, 
                               fx_test_classic_csv, 
                               fx_test_db,):
    stack=model.Stack(cfg.TransactionListBeta)
    if csv_type == 'alpha':
        stack.input_type = cfg.TransactionListClassic
        single_csv_1, single_csv_2 = fx_test_classic_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListClassic
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListClassic
    elif csv_type == 'beta':
        stack.input_type = cfg.TransactionListBeta
        single_csv_1, single_csv_2 = fx_test_beta_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListBeta
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListBeta
    else:
        assert False, "Invalid Parameter"
    assert isinstance(single_csv_1, pathlib.Path), f" fixture is not Path"
    # create data for import
    c_tr = []
    
    for gtr in csv_importer1.get_transactions():
        for ltr in gtr:
            assert isinstance(ltr, list), f"data from csv not a list {ltr}"
            c_tr.append(stack.create_transaction(ltr))
    assert len(c_tr) == 5, f"flase number of transactions retrived from csv {c_tr}"
    # try to push transaction to DB
    testrepo = repo.TransactionsRepo(fx_test_db)
    ctrbefore = testrepo.get_transaction_ctr()
    testrepo.add_transaction(c_tr[0])
    ctrafter = testrepo.get_transaction_ctr()
    assert (ctrafter - ctrbefore) == 1

def push_transactions(orm_handler, stack, csv_importer):
    hashes = []
    for ctr, transactions in enumerate(csv_importer.get_transactions()):
        # get transaction from csv
        for ctr_t, transaction_c in enumerate(transactions, 1):            
            # make transaction from csv
            transaction_m = stack.create_transaction(transaction_c)                     
            # push transaction to DB
            orm_handler.write_to_transactions(transaction_m)
            hashes.append(transaction_m.__hash__())
    return (ctr_t, hashes)
    

@pytest.mark.skip()
@pytest.mark.parametrize("csv_fixture, start, end, value, expected", [
    ('beta', '17.10.2023', '19.10.2023', -40, 5),  # 5 number of transactions
    ('alpha', '16.01.2023', '24.01.2023', -51, 5),   # 5 number of transactions
])
def test_CmdImportCsv(fx_test_beta_csv, fx_test_classic_csv, fx_test_db, csv_fixture, start, end, value, expected):
    # PREPARATION
    # create model
    stack=model.Stack(cfg.TransactionListBeta)  
    # parametrize test 
    if csv_fixture == 'alpha':
        stack.input_type = cfg.TransactionListClassic
        single_csv_1, single_csv_2 = fx_test_classic_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListClassic
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListClassic
        
    elif csv_fixture == 'beta':
        stack.input_type = cfg.TransactionListBeta
        single_csv_1, single_csv_2 = fx_test_beta_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListBeta
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListBeta
        
    else:
        assert False, "Invalid Parameter"
    assert isinstance(single_csv_1, pathlib.Path), f" fixture is not Path"


    orm = bugal_orm.BugalOrm(fx_test_db, 'sqlite')
    t_repo = repo.TransactionsRepo(orm)
    cmd = service.CmdImportNewCsv(orm, stack, csv_importer1)
    result = cmd.execute()

    assert result == expected, f"No transactions imported {result}"
    ctr_t = orm.get_transaction_ctr()
    ctr_h = orm.get_history_ctr()
    assert ctr_t == expected, f"number of stored transaction in DB is wrong {ctr_t}"
    assert ctr_h == 1, f"number of stored history in DB is wrong {ctr_h}"
    # test if history has the same start and end date from csv
    his_l = orm.read_history()
    his = his_l[0]
    date_format = "%d.%m.%Y"  # Das Format für "Tag-Monat-Jahr"
    end_date = datetime.strptime(end, date_format).date()
    start_date = datetime.strptime(start, date_format).date()
    assert his.min_date == start_date, f"false min date: {his.min_date} != {start_date}"
    assert his.max_date == end_date, f"false min date: {his.max_date} != {end_date}"
    # test imported value in DB is correct
    filter = {'date-after': start_date}
    tran_l = orm.read_transactions(filter)
    tran = tran_l[0]
    assert tran.value == value, f"false transaction value returned: {tran.value}"

    orm.close_connection()

@pytest.mark.skip()
@pytest.mark.parametrize("csv_fixture, expected", [
    ('beta', 5),  # 5 number of transactions
    ('alpha', 5),   # 5 number of transactions
])
def test_duplicate_transaction_import(fx_test_beta_csv, fx_test_classic_csv, fx_test_db, csv_fixture, expected):
    # PREPARATION
    # create model
    stack=model.Stack(cfg.TransactionListBeta)  
    # parametrize test 
    if csv_fixture == 'alpha':
        stack.input_type = cfg.TransactionListClassic
        single_csv_1, single_csv_2 = fx_test_classic_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListClassic
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListClassic
        
    elif csv_fixture == 'beta':
        stack.input_type = cfg.TransactionListBeta
        single_csv_1, single_csv_2 = fx_test_beta_csv
        # create data for csv handler 1
        csv_importer1 = handler.CSVImporter(single_csv_1)
        csv_importer1.input_type = cfg.TransactionListBeta
        history_data1 = csv_importer1.get_meta_data()
        # create data for csv handler 2
        csv_importer2 = handler.CSVImporter(single_csv_2)
        csv_importer2.input_type = cfg.TransactionListBeta
        
    else:
        assert False, "Invalid Parameter"
    assert isinstance(single_csv_1, pathlib.Path), f" fixture is not Path"
    history_data2 = csv_importer2.get_meta_data()
    
    # create ORM
    orm_handler = bugal_orm.BugalOrm(fx_test_db, 'sqlite')
    # get first the number of existing transactions for comparison
    t_ctr_orm_init = orm_handler.get_transaction_ctr()
    assert t_ctr_orm_init == 0, f"Flase transaction init value"
    # EXECUTION
    ctr_t, hashes = push_transactions(orm_handler, stack, csv_importer1)    
    assert ctr_t == expected, f"not all transactions generated {ctr_t}"
    unique = set(hashes)
    assert len(hashes) == len(unique), f"number of unique hashes is different"
    t_ctr_orm = orm_handler.get_transaction_ctr()
    assert t_ctr_orm == t_ctr_orm_init + 5, f"no transaction pushed {t_ctr_orm}"
    ctr_t, hashes = push_transactions(orm_handler, stack, csv_importer2)
    assert ctr_t == expected, f"not all transactions generated {ctr_t}"
    t_ctr_orm = orm_handler.get_transaction_ctr()
    assert t_ctr_orm == t_ctr_orm_init + 8, f"no transaction pushed {t_ctr_orm}"

