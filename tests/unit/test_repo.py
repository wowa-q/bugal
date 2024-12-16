# pylint: skip-file
# flake8: noqa
from datetime import datetime, date
import pathlib
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import pytest

 
from bugal.app.model import Stack
from bugal.app.model import Filter
from bugal.app import model
from bugal.db import repo, repo_adapter, orm
from cfg import config
from libs import exceptions as err


from fixtures import basic
from fixtures import model_fx
from fixtures import sql_fx
# from fixtures import orm_fx

FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"


# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, table", [
    ('sqlite', 'History'),
    ('sqlite', 'Transaction'),
    ('memory', 'History'),
    ('memory', 'Transaction'),   
    
])
def test_init_transaction_sqlrepo(repo_type, table, fx_new_db_file_name):
    # Preparation: static variables have to be reinitialized before testing
    orm.SqlTransactionRepo.__type__ = None
    orm.SqlTransactionRepo.__path__ = ''
    orm.SqlTransactionRepo.__instance__ = None
    orm.SqlHistoryRepo.__type__ = None
    orm.SqlHistoryRepo.__path__ = ''
    orm.SqlHistoryRepo.__instance__ = None

    if 'Transaction' in table:
        repo_ = orm.SqlTransactionRepo.get_instance()            
    else:
        repo_ = orm.SqlHistoryRepo.get_instance()
    assert repo_ is not None, f"Sql Repo not initialized"
    assert repo_.orm is not None, f"Sql Repo not initialized - no ORM"
    assert repo_.session is not None, f"Sql Repo not initialized - no session"
    assert repo_.engine is not None, f"Sql Repo not initialized - no engine"
    assert isinstance(repo_.session, Session), f"session has a wrong type"
    # type comes from configuration
    # assert repo_.__type__ == 'sqlite', f"Orm not initialized with default {repo_.__type__}"
    # assert repo_.__path__ == cfg.DBFILE, f"Orm not initialized with default {repo_.__path__} / {cfg.DBFILE}"
    
    # adjusting repo type and path    
    if 'Transaction' in table:
        orm.SqlTransactionRepo.__type__ = repo_type
        orm.SqlTransactionRepo.__path__ = os.curdir
        repo_ = orm.SqlTransactionRepo.get_instance()
        assert orm.SqlTransactionRepo.__path__ == os.curdir, f"Orm not initialized with repo path {repo_.__path__} / {os.curdir}"
        assert orm.SqlTransactionRepo.__type__ == repo_type, f"Orm not initialized with repo type {repo_.__type__}"
             
    else:
        orm.SqlHistoryRepo.__type__ = repo_type
        orm.SqlHistoryRepo.__path__ = os.curdir
        repo_ = orm.SqlHistoryRepo.get_instance()
        assert orm.SqlHistoryRepo.__path__ == os.curdir, f"Orm not initialized with repo path {repo_.__path__} / {os.curdir}"
        assert orm.SqlHistoryRepo.__type__ == repo_type, f"Orm not initialized with repo type {repo_.__type__}"
    
    assert repo_ is not None, f"Sql Repo not initialized"
    assert repo_.orm is not None, f"Sql Repo not initialized - no ORM"
    assert repo_.session is not None, f"Sql Repo not initialized - no session"
    assert repo_.engine is not None, f"Sql Repo not initialized - no engine"
    assert isinstance(repo_.session, Session), f"session has a wrong type"
    assert repo_.__path__ == os.curdir, f"Orm not initialized with repo path {repo_.__path__} / {os.curdir}"
    assert repo_.__type__ == repo_type, f"Orm not initialized with repo type {repo_.__type__}"
    
# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, expected", [
    ('memory', True),
    # ('sqlite', True),

])
def test_add_transaction_sqlrepo(repo_type, expected, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"Transaction is not DataClass type"
    orm_ = orm.Orm()
    orm_.delete_tables()
    if expected:
        if repo_type == 'sqlite' or repo_type == 'memory':
            orm.SqlTransactionRepo.__path__ = fx_test_db
            orm.SqlTransactionRepo.__type__ = repo_type
            rep = orm.SqlTransactionRepo()
        else:
            rep = repo.FakeRepo()
        tctr = rep.get_ctr()
        result = rep.add(fx_randomTransaction)
        tctr_after = rep.get_ctr()        
        assert result == expected, f"Transaction was not added as expected {result}"
        assert (tctr + 1) == tctr_after, f"No transaction added {tctr} - {tctr_after}"
        transaction = rep.get(hash_=hash(fx_randomTransaction))
        assert transaction is not None, f"No transaction retrived from DB {transaction}"
        assert transaction.id == 1, f"wrong Transaction id {transaction.id}"
        transaction = None
        transaction = rep.get(id_=1)
        assert transaction is not None, f"No transaction retrived from DB {transaction}"
        assert transaction.id == 1, f"wrong Transaction id {transaction.id}"
        rep.remove(hash_=hash(fx_randomTransaction))
        transaction = rep.get(hash_=hash(fx_randomTransaction))
        assert transaction is None, f"Delete of transaction from DB failed {transaction.id}"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, expected", [
    ('memory', True),
    # ('sqlite', True),

])
def test_add_history_sqlrepo(repo_type, expected, fx_history_unique, fx_test_db):
    # Preparation
    assert isinstance(fx_history_unique, model.History), f"History is not DataClass type"
    orm_ = orm.Orm()
    orm_.delete_tables()
    if expected:
        if repo_type == 'sqlite' or repo_type == 'memory':
            orm.SqlHistoryRepo.__path__ = fx_test_db
            orm.SqlHistoryRepo.__type__ = repo_type
            rep = orm.SqlHistoryRepo()
        else:
            rep = repo.FakeRepo()
        tctr = rep.get_ctr()
        result = rep.add(fx_history_unique)
        tctr_after = rep.get_ctr()        
        assert result == expected, f"history was not added as expected {result}"
        assert (tctr + 1) == tctr_after, f"No history added {tctr} - {tctr_after}"
        history = rep.get(hash_=fx_history_unique.checksum)
        assert history is not None, f"No history retrived from DB {history}"
        assert history.id == 1, f"wrong history id {history.id}"
        history = None
        history = rep.get(id_=1)
        assert history is not None, f"No history retrived from DB {history}"
        assert history.id == 1, f"wrong history id {history.id}"
        history = rep.get(1)
        assert history is None, f"Unknown history retrived from DB {history}"
        rep.remove(id_=1)
        history = rep.get(id_=1)
        assert history is None, f"Delete of history from DB failed {history.id}"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [
    
    #('sqlite'),    
    ('memory'),
])
def test_add_duplicate_transaction_sqlrepo(repo_type, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"Transaction is not DataClass type"
    if repo_type == 'sqlite' or repo_type == 'memory':
        orm.SqlTransactionRepo.__path__ = fx_test_db
        orm.SqlTransactionRepo.__type__ = repo_type
        rep = orm.SqlTransactionRepo()
    else:
        rep = repo.FakeRepo()
    rep.add(fx_randomTransaction)
    tctr = rep.get_ctr()
    hash1 = hash(fx_randomTransaction)
    with pytest.raises(err.ImportDuplicateTransaction):
        rep.add(fx_randomTransaction)
    tctr_after = rep.get_ctr()
    hash2 = hash(fx_randomTransaction)
    assert (tctr) == tctr_after, f"transaction added unexpected {tctr} {hash1} - {tctr_after} {hash2}"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [
    #('sqlite'),    
    ('memory'),
])
def test_add_false_type_transaction_sqlrepo(repo_type, fx_transaction_example_classic, fx_test_db):
    # Preparation
    if repo_type == 'sqlite' or repo_type == 'memory':
        orm.SqlTransactionRepo.__path__ = fx_test_db
        orm.SqlTransactionRepo.__type__ = repo_type
        rep = orm.SqlTransactionRepo()
    else:
        rep = repo.FakeRepo()

    with pytest.raises(err.NoValidTransactionData):
        rep.add(fx_transaction_example_classic)

# ADAPTER tests
# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type", [
    #('fake'),
    ('sqlite'),    
    ('memory'),
    
])
def test_init_repo_adapter(repo_type, fx_test_db):
    cfg_ = config.get_config()

    # Preparation: static variables have to be reinitialized before testing
    orm.SqlTransactionRepo.__type__ = None
    orm.SqlTransactionRepo.__path__ = ''
    orm.SqlTransactionRepo.__instance__ = None
    orm.SqlHistoryRepo.__type__ = None
    orm.SqlHistoryRepo.__path__ = ''
    orm.SqlHistoryRepo.__instance__ = None

    adapter = repo_adapter.RepoAdapter(fx_test_db, repo_type)
    assert adapter is not None, f"Adapter Repo not initialized"
    assert adapter.db_type == repo_type
    assert orm.SqlTransactionRepo.__path__ == fx_test_db, f"Orm not initialized with repo path by adapter {orm.SqlTransactionRepo.__path__} / {fx_test_db}"
    assert orm.SqlTransactionRepo.__type__ == repo_type, f"Orm not initialized with repo type by adapter {orm.SqlTransactionRepo.__type__}"
    assert orm.SqlHistoryRepo.__path__ == fx_test_db, f"Orm not initialized with repo path by adapter {orm.SqlHistoryRepo.__path__} / {fx_test_db}"
    assert orm.SqlHistoryRepo.__type__ == repo_type, f"Orm not initialized with repo type by adapter {orm.SqlHistoryRepo.__type__}"
    # only type to be parametrized
    adapter = repo_adapter.RepoAdapter(db_type=repo_type)
    assert adapter is not None, f"Adapter Repo not initialized"
    assert orm.SqlTransactionRepo.__type__ == repo_type, f"One parameter initialization failed {orm.SqlTransactionRepo.__type__}"
    assert orm.SqlHistoryRepo.__type__ == repo_type, f"One parameter initialization failed {orm.SqlHistoryRepo.__type__}"
    # repos have to be initialized to get defaut values
    orm.SqlTransactionRepo()
    orm.SqlHistoryRepo()
    assert orm.SqlTransactionRepo.__path__ == cfg_.dbpath, f"One parameter initialization failed {orm.SqlTransactionRepo.__path__} / {cfg.DBFILE}"
    assert orm.SqlHistoryRepo.__path__ == cfg_.dbpath, f"One parameter initialization failed: -> {orm.SqlHistoryRepo.__path__} / {cfg.DBFILE}"
    # without parameters - use default values
    adapter = repo_adapter.RepoAdapter()
    assert adapter is not None, f"Adapter Repo not initialized"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_, expected", [       
    ('memory', True),
    # ('fake', True),
])
def test_add_transaction_repo_adapter(repo_, expected, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"Transaction is not DataClass type"
    if expected:
        if repo_ == 'sqlite' or repo_ == 'memory':
            adapter = repo_adapter.RepoAdapter(fx_test_db, repo_)
        else:
            adapter = repo.FakeRepo()
        assert adapter.db_type == repo_, f"False repo type {adapter.db_type}"
        tctr = adapter.get_transaction_ctr()
        assert adapter.trepo is not None, f"Repo of Adapter not initialized {adapter.trepo}"
        result = adapter.add_transaction(fx_randomTransaction)
        
        tctr_after = adapter.get_transaction_ctr()
        assert result == expected, f"Transaction was not added as expected {result}"
        assert (tctr + 1) == tctr_after, f"No transaction added {tctr} - {tctr_after}"
        # pushing of the same transaction should raise an exception
        with pytest.raises(err.ImportDuplicateTransaction):
            adapter.add_transaction(fx_randomTransaction)

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    #('fake'),    
    ('sqlite'),
])
def test_add_false_type_transaction_repo_adapter(repo_type, fx_transaction_example_classic, fx_test_db):
    # Preparation
    if repo_type == 'sqlite' or repo_type == 'memory':
        adapter = repo_adapter.RepoAdapter(fx_test_db, repo_type)
    else:
        adapter = repo.FakeRepo()
    with pytest.raises(err.NoValidTransactionData):
        adapter.add_transaction(fx_transaction_example_classic)


# REPO tests
# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, table", [
    ('memory', 'Transaction'),
    ('sqlite', 'Transaction'),
    ('memory', 'History'),
    ('sqlite', 'History'),
])
def test_init_repo(repo_type, table, fx_test_db):
    if table == 'History':
        repo_ = repo.HistoryRepo(fx_test_db, repo_type)
    else:
        repo_ = repo.TransactionsRepo(fx_test_db, repo_type)
    assert repo_.adapter is not None, f"Repo Adapter is None"
    assert repo_.adapter.db_type == repo_type, f"Repo type adapter incorect {repo_.adapter.db_type}"
    assert repo_.adapter.pth == fx_test_db, f"Repo path adapter incorect {repo_.adapter.pth}"
    assert repo_.adapter.trepo is None, f"Transaction Repo initialized"
    assert repo_.adapter.hrepo is None, f"History Repo initialized"
    
    repo_ = repo.TransactionsRepo(fx_test_db)
    assert repo_.adapter is not None, f"Repo Adapter is None"
    repo_ = repo.TransactionsRepo()
    assert repo_.adapter is not None, f"Repo Adapter is None"
    
# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, expected", [       
    ('memory', True),
    # TODO test with physical DB
])
def test_add_transaction_repo(repo_type, expected, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"Transaction is not DataClass type"
    if expected:
        if repo_type == 'sqlite' or repo_type == 'memory':
            repo_ = repo.TransactionsRepo(fx_test_db, repo_type)
        else:
            repo_ = repo.FakeRepo()
        tctr = repo_.get_transaction_ctr()
        result = repo_.add_transaction(fx_randomTransaction)
        tctr_after = repo_.get_transaction_ctr()
        assert result == expected, f"Transaction was not added as expected {result}"
        assert (tctr + 1) == tctr_after, f"No transaction added {tctr} - {tctr_after}"
        transaction = repo_.get_transaction(id_=1)
        assert transaction is not None, f"transaction was not read {transaction}"
        if repo_type != 'fake':
            assert transaction.id == 1, f"transaction object with wrong id"
        # test checksum
        transaction = repo_.get_transaction(hash_=hash(fx_randomTransaction))
        assert transaction is not None, f"transaction was not read {transaction}"
        if repo_type != 'fake':
            assert str(transaction.checksum) == str(hash(fx_randomTransaction)), f"transaction object with wrong hash {transaction.checksum} / {hash(fx_new_betaTransaction)}"
        if repo_type != 'fake':
            # test range of transactions
            date1 = date(2020, 10, 19)
            date2 = date(2024, 10, 16)
            transactions = repo_.get_transaction(start_date=date1, end_date=date2)
            assert transactions is not None, f"transaction was not read {transactions}"
            assert len(transactions)==3, f"Number of transactions: {len(transactions)}"
            datum = transactions[0].datum
            assert isinstance(datum, date)
            assert str(datum) == '2022-01-01', f"first transaction has date: {datum}, was looking forgreater than {date1}"
            datum = transactions[0].datum
            assert str(datum) == '2022-01-01', f"first transaction has date: {datum}, was looking forgreater than {date2}"
            assert transactions[0].id != transactions[2].id, "Two transactions with the same ID"
            assert transactions[0].checksum != transactions[2].checksum, "Two transactions with the same checksum"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
  
    ('memory'),
])
def test_add_duplicate_transaction_repo(repo_type, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"Transaction is not DataClass type"
    if repo_type == 'sqlite' or repo_type == 'memory':
        repo_ = repo.TransactionsRepo(fx_test_db, repo_type)
    else:
        repo_ = repo.FakeRepo()
    repo_.add_transaction(fx_randomTransaction)
    tctr = repo_.get_transaction_ctr()
    hash1 = hash(fx_randomTransaction)
    with pytest.raises(err.ImportDuplicateTransaction):
        repo_.add_transaction(fx_randomTransaction)
    tctr_after = repo_.get_transaction_ctr()
    hash2 = hash(fx_randomTransaction)
    assert (tctr) == tctr_after, f"transaction added unexpected {tctr} {hash1} - {tctr_after} {hash2}"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    # ('fake'),    
    ('sqlite'),
])
def test_add_false_type_transaction_repo(repo_type, fx_transaction_example_classic, fx_test_db):
    # Preparation
    if repo_type == 'sqlite' or repo_type == 'memory':
        repo_ = repo.TransactionsRepo(fx_test_db, repo_type)
    else:
        repo_ = repo.FakeRepo()
    with pytest.raises(err.NoValidTransactionData):
        repo_.add_transaction(fx_transaction_example_classic)

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, expected", [       
    ('memory', True),
    # ('sqlite', True),
    # ('fake', True),
])
def test_add_history_repo(repo_type, expected, fx_history, fx_test_db):
    # Preparation
    assert isinstance(fx_history, model.History), f"History is not DataClass type"
    orm_ = orm.Orm.get_instance()
    orm_.delete_tables()
    if expected:
        if repo_type == 'sqlite' or repo_type == 'memory':
            repo_ = repo.HistoryRepo(fx_test_db, repo_type)
        else:
            repo_ = repo.FakeRepo()
        tctr = repo_.get_history_ctr()
        result = repo_.add_history(fx_history)
        tctr_after = repo_.get_history_ctr()
        assert result == expected, f"History was not added as expected {result}"
        assert (tctr + 1) == tctr_after, f"No History added {tctr} - {tctr_after}"
        history = repo_.get_history(id_=1)
        assert history is not None, f"History was not read {history}"
        if repo_type != 'fake':
            assert history.id == 1, f"history object with wrong id"
        history = repo_.get_history(hash_=fx_history.checksum)
        assert history is not None, f"History was not read {history}"
        if repo_type != 'fake':
            assert history.checksum == fx_history.checksum, f"history object with wrong hash"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    # ('fake'),    
    ('memory'),
])
def test_add_duplicate_history_repo(repo_type, fx_history_unique, fx_test_db):
    # Preparation
    assert isinstance(fx_history_unique, model.History), f"History is not DataClass type"
    orm_ = orm.Orm.get_instance()
    orm_.delete_tables()
    if repo_type == 'sqlite' or repo_type == 'memory':
        repo_ = repo.HistoryRepo(fx_test_db, repo_type)
    else:
        repo_ = repo.FakeRepo()
    repo_.add_history(fx_history_unique)
    tctr = repo_.get_history_ctr()
    hash1 = hash(fx_history_unique)
    with pytest.raises(err.ImportFileDuplicate):
        repo_.add_history(fx_history_unique)
    tctr_after = repo_.get_history_ctr()
    hash2 = hash(fx_history_unique)
    assert (tctr) == tctr_after, f"History added unexpected {tctr} {hash1} - {tctr_after} {hash2}"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    # ('fake'),    
    ('sqlite'),
])
def test_add_false_type_history_repo(repo_type, fx_transaction_example_classic, fx_test_db):
    # Preparation
    orm_ = orm.Orm.get_instance()
    orm_.delete_tables()
    if repo_type == 'sqlite' or repo_type == 'memory':
        repo_ = repo.HistoryRepo(fx_test_db, repo_type)
    else:
        repo_ = repo.FakeRepo()
    with pytest.raises(err.NoValidHistoryData):
        repo_.add_history(fx_transaction_example_classic)

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    # ('fake'),    
    ('memory'),
])
def test_delete_transaction_repo(repo_type, fx_randomTransaction, fx_test_db):
    # Preparation
    assert isinstance(fx_randomTransaction, model.Transaction), f"History is not DataClass type"
    orm_ = orm.Orm.get_instance()
    orm_.delete_tables()

    if repo_type in ['memory', 'sqlite']:
        repo_ = repo.TransactionsRepo(pth=fx_test_db, db_type=repo_type)        
    else:
        repo_ = repo.FakeRepo()

    repo_.add_transaction(fx_randomTransaction)
    ctr = repo_.get_transaction_ctr()
    assert ctr > 0, f"adding new History failed"
    result = repo_.del_transaction(id_=1)
    assert result == True, f"History Not deleted {result}"
    ctr_after = repo_.get_transaction_ctr()
    assert ctr > ctr_after, f"deleting failed"
    ctr = repo_.get_transaction_ctr()
    result = repo_.del_transaction(hash_=hash(fx_randomTransaction))
    assert result == True, f"History Not deleted {result}"
    ctr_after = repo_.get_transaction_ctr()
    assert ctr > ctr_after, f"deleting failed"

# @pytest.mark.skip()
@pytest.mark.parametrize("repo_type, ", [    
    # ('fake'),    
    ('memory'),
])
def test_delete_history_repo(repo_type, fx_history_unique, fx_test_db):
    # Preparation
    assert isinstance(fx_history_unique, model.History), f"History is not DataClass type"
    orm_ = orm.Orm.get_instance()
    orm_.delete_tables()

    if repo_type in ['memory', 'sqlite']:
        repo_ = repo.HistoryRepo(pth=fx_test_db, db_type=repo_type)        
    else:
        repo_ = repo.FakeRepo()

    repo_.add_history(fx_history_unique)
    ctr = repo_.get_history_ctr()
    assert ctr > 0, f"adding new History failed"
    result = repo_.del_history(id_=1)
    assert result == True, f"History Not deleted {result}"
    ctr_after = repo_.get_history_ctr()
    assert ctr > ctr_after, f"deleting failed"
    ctr = repo_.get_history_ctr()
    result = repo_.del_history(hash_=fx_history_unique.checksum)
    assert result == True, f"History Not deleted {result}"
    ctr_after = repo_.get_history_ctr()
    assert ctr > ctr_after, f"deleting failed"