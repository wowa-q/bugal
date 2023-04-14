# pylint: skip-file
from context import bugal

# from fixtures import basic
from bugal import cli

def test_return():
    assert cli.provide() == True

def test_fixtures(fx_month_data):
    assert cli.provide_list() == fx_month_data
 