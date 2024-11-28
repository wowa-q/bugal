# pylint: skip-file
# flake8: noqa

import pathlib
from datetime import datetime
from dataclasses import fields
import pytest

from context import bugal

from bugal import service as srvc
# from bugal import model
# from bugal import handler
# from bugal import repo
from bugal import config as cfg

from fixtures import basic
from fixtures import orm_fx
from fixtures import e2e_fx
from fixtures import fixtures as fx

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

beta_file = e2e_fx.fx_test_beta_csv
alpha_file = e2e_fx.fx_test_classic_csv

# @pytest.mark.skip()
@pytest.mark.parametrize("cfg_type, csv_type, pth", [
    ('user', 'beta', beta_file),    # user provides configuration
    # ('user', 'alpha', alpha_file),  # user provides configuration
    # ('static', '', ''),             # configuration from config file
    # ('user', 'beta', ''),           # user invalid config: path
    # ('user', 'alpha', ''),          # user invalid config: type
    # ('user', '', ''),               # user invalid config: empty
    # ('static', '', 'invalid'),      # static invalid config: path
    # ('static', 'invalid', ''),      # static invalid config: type
])
def test_importCsv_service(cfg_type,
                           csv_type,
                           pth,
                           ):
    # use service API to import csv
    # no error
    # what is expected?
    if cfg_type == 'static':
        import_cfg = cfg.get_config()
        if pth == 'invalid':
            # test path validation handler
            assert True
        if csv_type == 'invalid':
            # test input type validation handler
            assert True
    else:
        import_cfg = cfg.get_config()
        import_cfg.path_ = pth
        import_cfg.import_type = csv_type
    assert import_cfg is not None, f"No configuration received: {import_cfg}"
    assert import_cfg.import_type != "", f"no import_type received {import_cfg.import_type}"
    assert import_cfg.path_ == "", f"Empty path received {import_cfg.path_}"
    message = srvc.import_data(import_cfg)
    assert message is not None, f"message received: {message}"
