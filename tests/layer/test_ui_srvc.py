# pylint: skip-file
# flake8: noqa
from datetime import datetime, date
import pathlib
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import pytest

from fixtures.fx import fx_test_classic_csv, fx_test_beta_csv

from bugal.cfg import config as cfg
from bugal.srvc import service as srvc

FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"



# @pytest.mark.skip()
@pytest.mark.parametrize("cfg_type, csv_type, pth", [
    ('user', 'beta', 'beta'),    # user provides configuration
    ('user', 'alpha', 'alpha'),  # user provides configuration
    ('static', '', ''),             # configuration from config file
    ('user', 'beta', ''),           # user invalid config: path
    ('user', 'alpha', ''),          # user invalid config: type
    ('user', '', ''),               # user invalid config: empty
    # ('static', '', 'invalid'),      # static invalid config: path
    # ('static', 'invalid', ''),      # static invalid config: type
])
def test_importCsv_service(cfg_type,
                           csv_type,
                           pth,
                           fx_test_classic_csv,
                           fx_test_beta_csv
                           ):
    # test fixtures:
    assert fx_test_classic_csv[0].is_file(), f"Fixture is not a file: {fx_test_classic_csv}"
    assert fx_test_beta_csv[0].is_file(), f"Fixture is not a file: {fx_test_beta_csv}"
    # use service API to import csv
    # no error
    # what is expected?
    import_cfg = cfg.get_config()
    if cfg_type == 'static':
        test_msg = 'Import successful'
        import_cfg = cfg.get_config()
        if pth == 'invalid':
            # test path validation handler
            assert True
        if csv_type == 'invalid':
            # test input type validation handler
            assert True
    else:
        if csv_type == 'beta':
            file_ = fx_test_beta_csv[0]
            test_msg = 'Import successful'
        elif csv_type == 'alpha':
            file_ = fx_test_classic_csv[0]
            test_msg = 'Import successful'
        else:
            file_ = None
            test_msg = 'Can not to parse the file path'
        
        import_cfg.path_ = file_
        import_cfg.import_type = csv_type

    message = srvc.import_data(import_cfg)
    assert message is not None, f"message received: {message}"
    assert test_msg in message, message
