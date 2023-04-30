# pylint: skip-file
from datetime import date

import pytest

from context import bugal

from bugal import model
from bugal import repo

def test_transaction_hash_equality():
    t1 = model.Transaction("2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t2 = model.Transaction("2022-01-01", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    t3 = model.Transaction("2022-01-02", "2022-01-01", "text", "debitor", "verwendung", "konto", "blz", 10, "debitor_id", "mandats_ref", "customer_ref", "src_konto")
    assert t1 == t2, "Two equel transaction objects must have equal hash value"
    assert t1 != t3, "Different hash value due to different objects"

#@pytest.mark.skip()
def test_transaction_creation(fx_transaction_example):
    stack=model.Stack()
    stack.create_transaction(fx_transaction_example)

#@pytest.mark.skip()
def test_transaction_equality_for_every_par(fx_transaction_example):
    stack=model.Stack()
    t1 = stack.create_transaction(fx_transaction_example)
    data = fx_transaction_example
    for ind, _ in enumerate(fx_transaction_example):
        data[ind] = "changed"
        t2 = stack.create_transaction(data)
        assert t1 != t2, f"Parameter {ind} changed"

#@pytest.mark.skip()
def test_create_transactions_list(fx_transactions_list_example):
    stack=model.Stack()
    for line in fx_transactions_list_example:
        stack.create_transaction(line)
    
    assert len(fx_transactions_list_example) == 5

#@pytest.mark.skip()
def test_store_transactions_in_db(fx_transactions_list_example):
    stack=model.Stack()
    assert len(stack.transactions) == 0

    for line in fx_transactions_list_example:
        stack.create_transaction(line)
    stack.push_transactions()
    # one transaction is double and will be removed from the list before push
    assert len(stack.transactions) == 4
    assert stack.filter.max_date == date.fromisoformat("2022-01-04")
    assert stack.filter.min_date == date.fromisoformat("2022-01-01")
