import pytest
import pathlib
from datetime import datetime

from context import bugal

from bugal import exceptions as err
from bugal.model import Transaction, History
from bugal.csv_adapter import InputMaster, ClassicInput, ModernInput, DailyCard, ImporterAdapter

from fixtures import basic
from fixtures import csv_fx


@pytest.fixture
def classic_input(fx_single_csv):
    return ClassicInput(fx_single_csv)

@pytest.fixture
def modern_input(fx_single_csv_new):
    return ModernInput(pathlib.Path(fx_single_csv_new))

@pytest.fixture
def dailycard_input():
    return DailyCard(pathlib.Path('dailycard_test.csv'))

# @pytest.mark.skip()
def test_get_checksum(classic_input, fx_single_csv):
    assert isinstance(fx_single_csv, pathlib.Path)
    checksum = classic_input.get_checksum(fx_single_csv)
    assert checksum == '59F458B36454B4A06210778C75806961'  # Ersetze 'EXPECTED_CHECKSUM' durch den erwarteten Wert

# @pytest.mark.skip()
def test_read_lines(classic_input, fx_single_csv):
    lines = list(classic_input.read_lines(fx_single_csv))
    assert len(lines) > 0
    # f.write('"24.01.2023";"24.01.2023";
    # "Classic";"PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV";
    # "LU89751000135104200E";"PPLXLUL2";"-51,00";"LU96ZZZ0000000000000000058";"";"1024853056047";\n')
    # assert lines[1] == ['24.01.2023', 
    #                     'Classic', 'PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV', 
    #                     'Test Verwendung', 
    #                     'LU89751000135104200E', 
    #                     '-51,00', 
    #                     'LU96ZZZ0000000000000000058', 
    #                     '', 
    #                     '1024853056047']

# @pytest.mark.skip()
def test_get_meta_data(classic_input):
    meta = classic_input.get_meta_data()
    assert meta['file_name'] == 'single', f"File name extracted: {meta['file_name']}"
    assert meta['file_ext'] == 'csv'
    assert meta['start_date'] == datetime.strptime('16.01.2023', "%d.%m.%Y")
    assert meta['end_date'] == datetime.strptime('24.01.2023', "%d.%m.%Y")
    assert meta['account'] == 'DE12345300001019363165' 

@pytest.mark.skip()
def test_classic_input_transaction(classic_input):
    classic_input.get_meta_data()
    transactions = list(classic_input.get_transaction())
    assert len(transactions) == 5
    trans = transactions[0]
    assert isinstance(trans, Transaction)
    assert trans.date == datetime.strptime('24.01.2023', "%d.%m.%Y")

@pytest.mark.skip()
def test_modern_input_transaction(modern_input):
    modern_input.get_meta_data()
    transactions = list(modern_input.get_transaction())
    assert len(transactions) == 6, f"Transaction read from csv: {len(transactions)}, expected 6"
    trans = transactions[0]
    assert isinstance(trans, Transaction)
    assert trans.date == datetime.strptime('19.10.23', "%d.%m.%y")

@pytest.mark.skip() # fixture fehlt
def test_dailycard_input_transaction(dailycard_input):
    transactions = list(dailycard_input.get_transaction())
    assert len(transactions) == 1
    trans = transactions[0]
    assert isinstance(trans, Transaction)
    assert trans.date == datetime.strptime('01.01.2023', "%d.%m.%Y")

# @pytest.mark.skip()
def test_importer_adapter_classic(fx_single_csv):
    adapter = ImporterAdapter(fx_single_csv)
    meta = adapter.get_meta_from_classic()
    assert meta['file_name'] == 'single'
    assert meta['file_ext'] == 'csv'
    his = adapter.get_history_from_classic(meta)
    assert isinstance(his, History), f"Got hist of type: {type(his)}"

# @pytest.mark.skip()
def test_importer_adapter_modern(fx_single_csv_new):
    adapter = ImporterAdapter(fx_single_csv_new)
    meta = adapter.get_meta_from_modern()
    assert meta['file_name'] == 'single_new'
    assert meta['file_ext'] == 'csv'

@pytest.mark.skip() # fixture fehlt
def test_importer_adapter_dcard():
    adapter = ImporterAdapter('dailycard_test.csv')
    meta = adapter.get_meta_from_dcard()
    assert meta['file_name'] == 'dailycard_test'
    assert meta['file_ext'] == 'csv'
