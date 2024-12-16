# pylint: skip-file
# flake8: noqa

from datetime import date, datetime
import pathlib
import pytest

from bugal.app import csv_handler 
from bugal.app.model import Stack
from bugal.app.model import Filter
from bugal.app import model
from cfg import config
from libs import exceptions as err


from fixtures import basic
from fixtures import csv_fx
from fixtures import model_fx


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

# @pytest.mark.skip()
# @pytest.mark.parametrize("csv_type", [
#     ('classic'),
    # ('beta'),
    # ('2024'),
    # ('daily'),   
# ])
def test_init_stack(fx_single_csv):
    s = Stack('classic')
    assert isinstance(s.transactions, list)
    assert len(s.transactions) == 0
    assert isinstance(s.checksums, set)
    assert len(s.checksums) == 0
    assert isinstance(s.filter, Filter), f"Der Typ ist : {type(s.filter)}"
    assert s.nr_transactions == 0
    assert s.src_account == ''
    assert s.repo_type == 'sqlite'
    assert s.trepo is None
    assert s.hrepo is None
    assert s.import_meta is None
    assert s.history is None
    assert s.import_adapter is None

# @pytest.mark.skip()
@pytest.mark.parametrize("datum, expected", [
    ('invalid', 'Error'),   # invalid date format
    ('010101', 'Error'),   # invalid date format
    ('1a.10.23', 'Error'),   # invalid date format
    ('01.01.2023', 'OK'),   # valid date format
])
def test_invalid_date_handling(datum, expected, caplog):
    stack=model.Stack('TransactionListBeta')
    if expected == 'Error':
        with pytest.raises(err.InvalidTimeFormat):
            stack._make_date(datum)
        # test the original date is placed into the log
        assert datum in caplog.text
    else:
        result_date = stack._make_date(datum)
        # Überprüfen, ob das Ergebnis ein 'date'-Objekt ist und den erwarteten Wert hat
        assert isinstance(result_date, date)
        assert result_date == date(2023, 1, 1)

def test_create_history(fx_csv_meta_dict):
    s = Stack('classic')
    his = s.create_history(fx_csv_meta_dict)
    assert isinstance(his, model.History)
    assert isinstance(his.min_date, date)
    assert isinstance(his.import_date, date)
    assert isinstance(his.max_date, date)
    assert his.account == 'DE123456789'
    assert his.file_name == 'fx_dict'
    assert his.file_type == 'csv'
    assert his.checksum == ''
    # assert his.import_date == datetime.now()
    assert his.max_date == datetime.strptime('22.09.2023', '%d.%m.%Y').date()
    assert his.min_date == datetime.strptime('21.09.2023', '%d.%m.%Y').date()
    assert s.src_account == his.account
    assert s.import_meta == his, f"Stack has wrong meta: {s.import_meta}"

    with pytest.raises(err.NoValidHistoryData):
        s.create_history('')
    
    s.init_stack()
    assert s.src_account == ''


def test_create_transaction(fx_transaction_example_classic):
    h = csv_handler.ClassicInputAdapter('fx_single_csv')
    h.src_account = '12345'
    assert fx_transaction_example_classic[0]=="01.01.2022"
    dtran = h._make_transaction(fx_transaction_example_classic)
    s = Stack('classic')
    s.src_account = h.src_account
    tran = s.create_transaction(dtran)
    assert tran is not None
    assert isinstance(tran, model.Transaction)
    assert tran.src_konto == h.src_account
    assert len(s.checksums) > 0
    assert len(s.transactions) > 0
    assert s.nr_transactions == 1


# @pytest.mark.skip()
def test_transaction_equality_for_every_par(fx_transaction_example_classic):
    # prepare tests - transaction as a dict
    h = csv_handler.ClassicInputAdapter('fx_single_csv')
    h.src_account = '12345'
    dtran = h._make_transaction(fx_transaction_example_classic)

    stack=model.Stack('TransactionListClassic')
    t1 = stack.create_transaction(dtran)
    t3 = stack.create_transaction(dtran)
    dtran['tdate'] = "01.01.2002"
    t2 = stack.create_transaction(dtran)
    assert t1 == t3, f"Transactions are not equal {t1} vs. {t3} "
    assert t1 != t2, f"Transactions are still equal t1: {t1} '\n' t2: {t2}"
    
    assert hash(t1) == hash(t1), "new hash calculated for the same transaction"
    assert hash(t1) == hash(t3), "new hash calculated for the same transaction"
    assert hash(t1) != hash(t2), "same hash calculated for different transaction"