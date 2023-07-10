# pylint: skip-file
# flake8: noqa

from datetime import date

import pytest

from context import bugal

from bugal import model
from bugal import cfg

def test_transaction_hash_equality():
    t1 = model.Transaction("2022-01-01", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t2 = model.Transaction("2022-01-01", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t3 = model.Transaction("2022-01-02", "text", "status", "debitor", "verwendung", "konto", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    assert t1 == t2, "Two equel transaction objects must have equal hash value"
    assert t1 != t3, "Different hash value due to different objects"

# @pytest.mark.skip()
def test_transaction_creation(fx_transaction_example_classic):
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    stack.create_transaction(fx_transaction_example_classic)
    

# @pytest.mark.skip()
def test_transaction_creation_beta(fx_transaction_example_beta):
    stack=model.Stack()
    stack.input_type = cfg.TransactionListBeta
    stack.create_transaction(fx_transaction_example_beta)

# @pytest.mark.skip()
def test_transaction_equality_for_every_par(fx_transaction_example_classic):
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    t1 = stack.create_transaction(fx_transaction_example_classic)
    data = fx_transaction_example_classic
    for ind, _ in enumerate(fx_transaction_example_classic):
        data[ind] = "changed"
        t2 = stack.create_transaction(data)
        assert t1 != t2, f"Parameter {ind} changed"

# @pytest.mark.skip()
def test_create_transactions_list(fx_transactions_list_example_classic):
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    
    assert len(fx_transactions_list_example_classic) == 5

# @pytest.mark.skip()
def test_store_transactions_in_db(fx_transactions_list_example_classic):
    stack=model.Stack()
    stack.input_type = cfg.TransactionListClassic
    assert len(stack.transactions) == 0

    for line in fx_transactions_list_example_classic:
        stack.create_transaction(line)
    stack.push_transactions()
    # one transaction is double and will be removed from the list before push
    assert len(stack.transactions) == 4
    assert stack.filter.max_date == date.fromisoformat("2022-01-04")
    assert stack.filter.min_date == date.fromisoformat("2022-01-01")

# @pytest.mark.skip()
def test_store_import_history_in_db(fx_import_history):
    stack=model.Stack()
    stack.update_history(fx_import_history)

# TODO Test history automatically updated, when DB is changed