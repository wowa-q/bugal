# pylint: skip-file
# flake8: noqa

import pathlib

from fixtures.fx import fx_test_db
from fixtures.fx import fx_test_classic_csv
from fixtures.fx import fx_test_beta_csv


# from fixtures.basic import fx_month_data
# from fixtures.basic import fx_xls_file
# from fixtures.basic import fx_mandatory_sheets

# from fixtures.basic import fx_export_filter_aggregate

# from fixtures.csv_fx import fx_single_csv
# from fixtures.csv_fx import fx_single_csv_new
# from fixtures.csv_fx import fx_single_csv_single_line
# from fixtures.csv_fx import fx_banch_of_csv
# from fixtures.csv_fx import fx_single_invalid_csv
# from fixtures.csv_fx import fx_banch_of_invalid_csv
# from fixtures.csv_fx import fx_zip_archive
# from fixtures.csv_fx import fx_zip_archive_configured
# from fixtures.csv_fx import fx_csv_broken_date_classic
# from fixtures.csv_fx import fx_csv_broken_date_beta


# from fixtures.model_fx import fx_transaction_example_classic
# from fixtures.model_fx import fx_transactions_list_example_classic
# from fixtures.model_fx import fx_transaction_example_beta
# from fixtures.model_fx import fx_transactions_list_example_beta
# from fixtures.model_fx import fx_stack_example
# from fixtures.model_fx import fx_import_history
# from fixtures.model_fx import fx_csv_meta_dict

# from fixtures.sql_fx import fx_new_db_file_name
# from fixtures.sql_fx import fx_new_betaTransaction
# from fixtures.sql_fx import fx_new_classicTransactions_banch
# from fixtures.sql_fx import fx_new_betaTransactions_banch
# from fixtures.sql_fx import fx_history
# from fixtures.sql_fx import fx_history_unique
# from fixtures.sql_fx import fx_transaction_unique
# from fixtures.sql_fx import fx_checksum_repo_not_exist
# from fixtures.sql_fx import fx_checksum_repo_exist


# # from fixtures.orm_fx import fx_test_db_new
# # from fixtures.orm_fx import session
# # from fixtures.orm_fx import in_memory_db


FIXTURE_DIR = pathlib.Path(__file__).resolve() / "fixtures"
