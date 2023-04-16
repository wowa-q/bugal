import os 
import pathlib

import pytest


from context import bugal
from fixtures.basic import fx_month_data

from bugal import cli


FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"

@pytest.fixture
def fx_single_csv():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single.csv', 'w') as f:
        f.write('a,b,c')
        pth = FIXTURE_DIR / 'single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass

    
    return pth

@pytest.fixture
def fx_banch_of_csv():
    pth = FIXTURE_DIR / 'csv'
    try:
        pth.mkdir()
        for n in range(3):
            name = 'single_'+str(n)+'.csv'
            with open(pth / name, 'w') as f:
                f.write('a,b,c')
    except FileExistsError:
        pass  

    yield pth

    try:
        flist = pth.glob('*.csv')
        for f in flist:
            f.unlink()
        pathlib.Path(pth).rmdir()
    except PermissionError:
        pass

@pytest.fixture
def fx_export_filter_aggregate():
    fil = None
    return fil


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