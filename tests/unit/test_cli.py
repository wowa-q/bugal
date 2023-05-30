# pylint: skip-file
# flake8: noqa

import os 
import pathlib

import pytest


from context import bugal
from fixtures.basic import fx_month_data
# DUT import
from bugal import cli


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

def test_import_single_csv(fx_single_csv):
    result = cli.import_csv(fx_single_csv)
    assert result[0] == True, f"csv import failed: {result[1]}"

def test_import_banch_of_csv(fx_banch_of_csv):

    result = cli.import_csv(fx_banch_of_csv)
    assert result[0] == True, f"csv import failed: {result[1]}"

def test_export_excel(fx_export_filter_aggregate):
    result = cli.export_excel(fx_export_filter_aggregate)
    assert result[0] == True, f"Excel export reported as failed"
    # assert 'Bugalter.xlsx' in FIXTURE_DIR.glob('*.xlsx')

def test_import_excel(fx_export_filter_aggregate):
    result = cli.import_excel(fx_export_filter_aggregate)
    assert result[0] == True, f"Excel import reported as failed"

