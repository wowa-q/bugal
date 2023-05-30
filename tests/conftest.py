# pylint: skip-file
import pathlib

from fixtures.basic import fx_month_data
from fixtures.basic import fx_transaction_example
from fixtures.basic import fx_transactions_list_example
from fixtures.basic import fx_xls_file
from fixtures.basic import fx_mandatory_sheets
from fixtures.basic import fx_stack_example
from fixtures.basic import fx_export_filter_aggregate

from fixtures.csv_fx import fx_single_csv
from fixtures.csv_fx import fx_banch_of_csv
from fixtures.csv_fx import fx_single_invalid_csv
from fixtures.csv_fx import fx_banch_of_invalid_csv
from fixtures.csv_fx import fx_zip_archive

FIXTURE_DIR = pathlib.Path(__file__).resolve() / "fixtures"
