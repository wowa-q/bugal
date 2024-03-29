# pylint: skip-file
# flake8: noqa

from datetime import date
from datetime import datetime

import pytest

from context import bugal

from bugal import model
from bugal import cfg
from bugal import exceptions as err

def test_transaction_hash_equality(fx_transaction_example_classic):
    t1 = model.Transaction("2022.01.01", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t2 = model.Transaction("2022.01.01", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t3 = model.Transaction("2022.01.02", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    assert t1 == t2, "Two equel transaction objects must have equal hash value"
    assert t1 != t3, "Different hash value due to different objects"
    stack=model.Stack(cfg.TransactionListClassic)
    stack.set_src_account('')
    transaction1 = stack.create_transaction(fx_transaction_example_classic)
    transaction2 = stack.create_transaction(fx_transaction_example_classic)
    fx_transaction_example_classic[2] = "new text"
    transaction3 = stack.create_transaction(fx_transaction_example_classic)
    assert transaction1 == transaction2, "Two equel transaction objects must have equal hash value"
    assert transaction1 != transaction3, "Different hash value due to different objects"

#@pytest.mark.skip()
def test_transaction_creation(fx_transaction_example_classic):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    stack.set_src_account('src_konto') # history not available in that test -> needs to be created manually
    transaction = stack.create_transaction(fx_transaction_example_classic)
    assert isinstance(transaction.date, date), f"Transaction date wrong type: {transaction.date}"
    #assert transaction.date ==  datetime.date(2022, 1, 1), f"Transaction date {transaction.date}"
    datum = "01.01.2022"
    assert transaction.date == datetime.strptime(datum, '%d.%m.%Y').date()
    assert transaction.text ==  'text', f"Transaction text {transaction.text}"
    assert transaction.status ==  '-', f"Transaction status {transaction.status}"
    assert transaction.debitor ==  'debitor', f"Transaction debitor {transaction.debitor}"
    assert transaction.verwendung ==  'verwendung', f"Transaction verwendung {transaction.verwendung}"
    assert transaction.konto ==  'konto', f"Transaction konto {transaction.konto}"
    assert transaction.value ==  10, f"Transaction value {transaction.value}"
    assert transaction.debitor_id ==  'debitor_id', f"Transaction debitor_id {transaction.debitor_id}"
    assert transaction.mandats_ref ==  'mandats_ref', f"Transaction mandats_ref {transaction.mandats_ref}"
    assert transaction.customer_ref ==  'customer_ref', f"Transaction customer_ref {transaction.customer_ref}"
    assert transaction.src_konto ==  'src_konto', f"Transaction src_konto {transaction.src_konto}"
    
# @pytest.mark.skip()
def test_transaction_creation_beta(fx_transaction_example_beta):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListBeta
    sums1 = len(stack.checksums)
    trns1 = stack.nr_transactions
    stack.set_src_account('1234')
    transaction = stack.create_transaction(fx_transaction_example_beta)
    sums2 = len(stack.checksums)
    trns2 = stack.nr_transactions
    acc = stack.src_account
    assert sums2 != 0, f"No new checksums created {sums2}"
    assert sums2 > sums1, f"No new checksums created {sums2} > {sums1}"
    assert trns2 != 0, f"No new transactions created {trns2}"
    assert trns2 > trns1, f"No new transactions created {trns2} > {trns1}"
    assert acc == '1234', f"source account not updated {acc}"
    stack.init_stack()
    trns2 = stack.nr_transactions
    sums2 = len(stack.checksums)
    acc = stack.src_account
    assert sums2 == 0, f"No new checksums created {sums2}"
    assert trns2 == 0, f"No new transactions created {trns2}"
    assert acc == '', f"source account not updated {acc}"
    datum = "19.10.23"

    assert transaction.date == datetime.strptime(datum, '%d.%m.%y').date()
    assert transaction.text ==  '-', f"Transaction text {transaction.text}"
    assert transaction.status ==  'Gebucht', f"Transaction status {transaction.status}"
    assert transaction.debitor ==  'Angelina Merkel', f"Transaction debitor {transaction.debitor}"
    assert transaction.verwendung ==  '', f"Transaction verwendung {transaction.verwendung}"
    assert transaction.konto ==  '-', f"Transaction konto {transaction.konto}"
    
    assert transaction.debitor_id ==  '', f"Transaction debitor_id {transaction.debitor_id}"
    assert transaction.mandats_ref ==  '', f"Transaction mandats_ref {transaction.mandats_ref}"
    assert transaction.customer_ref ==  '', f"Transaction customer_ref {transaction.customer_ref}"
    assert transaction.src_konto ==  '1234', f"Transaction src_konto {transaction.src_konto}"
    assert isinstance(transaction.value, float), f"Transaction value is not Integer"
    assert transaction.value ==  -40, f"Transaction value {transaction.value}"

# @pytest.mark.skip()
def test_transaction_equality_for_every_par(fx_transaction_example_classic):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    t1 = stack.create_transaction(fx_transaction_example_classic)
    t3 = stack.create_transaction(fx_transaction_example_classic)
    data = fx_transaction_example_classic
    for ind, _ in enumerate(fx_transaction_example_classic):
        data[ind] = "20.12.1918"
        t2 = stack.create_transaction(data)
        assert t1 != t2, f"Parameter {ind} changed"
    assert hash(t1) == hash(t1), f"new hash calculated for the same transaction"
    assert hash(t1) == hash(t3), f"new hash calculated for the same transaction"

# @pytest.mark.skip()
def test_create_transactions_list(fx_transactions_list_example_classic):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    
    assert len(fx_transactions_list_example_classic) == 5

# @pytest.mark.skip()
def test_create_transactions_list_beta(fx_transactions_list_example_beta):
    stack=model.Stack(cfg.TransactionListBeta)
    stack.input_type = cfg.TransactionListBeta
    for line in fx_transactions_list_example_beta:
        stack.create_transaction(line)
    
    assert len(fx_transactions_list_example_beta) == 6
    assert len(stack.transactions) == 4
    assert stack.nr_transactions == 4

@pytest.mark.skip()
def test_store_transactions_in_db(fx_transactions_list_example_classic):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    assert len(stack.transactions) == 0

    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    stack.push_transactions('')
    # one transaction is double and will be removed from the list before push
    assert len(stack.transactions) == 4
    assert stack.filter.max_date == date.fromisoformat("2022-01-04")
    assert stack.filter.min_date == date.fromisoformat("2022-01-01")
    # TODO Test history automatically updated, when DB is changed

# @pytest.mark.skip()
def test_create_history(fx_csv_meta_dict):
    stack=model.Stack(cfg.TransactionListClassic)
    stack.input_type = cfg.TransactionListClassic
    assert len(stack.transactions) == 0
    assert isinstance(fx_csv_meta_dict, dict)
    # just to check test preconditions
    assert fx_csv_meta_dict.get('file_name') == 'fx_dict'
    
    his = stack.create_history(fx_csv_meta_dict)
    acc = stack.src_account
    assert isinstance(his, model.History)
    # min = datetime.strptime('21.09.2023', '%d.%m.%Y').date()
    # max = datetime.strptime('22.09.2023', '%d.%m.%Y').date()
    min = datetime.strptime(fx_csv_meta_dict.get('start_date'), '%d.%m.%Y').date()
    max = datetime.strptime(fx_csv_meta_dict.get('end_date'), '%d.%m.%Y').date()
    assert '21.09.2023' == fx_csv_meta_dict.get('start_date'), f"Dict start date: {min}"
    assert '22.09.2023' == fx_csv_meta_dict.get('end_date'), f"Dict end date: {max}"
    
    assert his.min_date == min, f"History start date: {his.min_date}"
    assert his.max_date == max, f"History end date: {his.max_date}"
    assert acc == 'DE123456789', f"source account not updated {acc}"
    stack.init_stack()
    acc = stack.src_account
    assert acc == '', f"source account not updated {acc}"

#@pytest.mark.skip()
def test_init_stack():
    # creaste a stack
    beta_stack=model.Stack(cfg.TransactionListBeta)
    classic_stack=model.Stack(cfg.TransactionListClassic)
    assert beta_stack.transactions is not None
    assert beta_stack.checksums is not None
    assert beta_stack.filter is not None
    assert beta_stack.nr_transactions is not None
    assert beta_stack.input_type == cfg.TransactionListBeta
    assert beta_stack.src_account is not None
    
    assert classic_stack.transactions is not None
    assert classic_stack.checksums is not None
    assert classic_stack.filter is not None
    assert classic_stack.nr_transactions is not None
    assert classic_stack.input_type == cfg.TransactionListClassic
    assert classic_stack.src_account is not None

@pytest.mark.skip()
def test_store_import_history_in_db(fx_import_history):
    stack=model.Stack(cfg.TransactionListBeta)
    stack.update_history(fx_import_history)
    assert False, f"Not implemented"
    meta = cfg.CSV_META.copy()

def check_behavior():
    date_str = "1a1023"
    date_obj = datetime.strptime(date_str, "%d.%m.%y")

# @pytest.mark.skip()
@pytest.mark.parametrize("datum, expected", [
    ('invalid', 'Error'),   # invalid date format
    ('010101', 'Error'),   # invalid date format
    ('1a.10.23', 'Error'),   # invalid date format
    ('01.01.2023', 'OK'),   # valid date format
])
def test_invalid_date_handling(datum, expected, caplog):
    stack=model.Stack(cfg.TransactionListBeta)
    if expected == 'Error':
        with pytest.raises(ValueError):
            stack._make_date(datum)
        # test the original date is placed into the log
        assert datum in caplog.text
    else:
        result_date = stack._make_date(datum)
        # Überprüfen, ob das Ergebnis ein 'date'-Objekt ist und den erwarteten Wert hat
        assert isinstance(result_date, date)
        assert result_date == date(2023, 1, 1)
        
data_ = ["01.01.2022", "01.01.2022", "text", "debitor", "verwendung", "konto", "blz", "10", "debitor_id", "mandats_ref", "customer_ref", "src_konto"]
dataset = set(data_)
# @pytest.mark.skip()
@pytest.mark.parametrize("data, expected", [
    ('invalid', 'input_type'),   
    ('010101', 'input_type'),   
    ('1a.10.23', 'input_type'),   
    (dataset, 'list'),
    ([1,2,3,], 'list'),
    (data_, 'DATE'),
    (data_, 'src_account'),
    (data_, 'OK'),  
])
def test_invalid_data_transaction(data, expected):
    stack=model.Stack(cfg.TransactionListBeta)
    
    if expected == 'input_type':
        stack.init_stack()
        with pytest.raises(err.NoInputTypeSet):
            stack.create_transaction(data)
    elif expected == 'list':
        with pytest.raises(err.NoValidTransactionData):
            stack.create_transaction(data)
    elif expected == 'DATE':
        stack.input_type = data # just something which is not None
        with pytest.raises(AttributeError):
            stack.create_transaction(data)
    elif expected == 'src_account':
        stack.src_account = None

        with pytest.raises(err.NoValidTransactionData):
            stack.create_transaction(data)
    else:
        result_date = stack.create_transaction(data)
        assert result_date is not None

