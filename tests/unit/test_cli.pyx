# pylint: skip-file
# flake8: noqa

import os 
import pathlib
from subprocess import Popen, PIPE
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from context import bugal
from fixtures import basic
from fixtures import orm_fx
from fixtures import sql_fx
# DUT import
from bugal import cli



FIXTURE_DIR = pathlib.Path(__file__).parent.parent.resolve() / "fixtures"
@pytest.fixture
def mock_subprocess():
    with patch('subprocess.Popen') as mock_popen:
        yield mock_popen

# positiv test
@pytest.mark.parametrize(
    "options",
    [
        ("--cmd", "import", "-csv", "test_csv.csv", "-v", "classic"),
        ("--cmd", "import", "-csv", "test_csv.csv","--variant", "beta"),
        ("-cmd", "import", "-csv", "test_csv.csv","-v", "beta"),        
    ],
)

def test_cli_with_system_exit_code_0(options):
    cli.TEST = True
    runner = CliRunner()

    result = runner.invoke(cli.execute, options)

    assert result.exit_code == 0, f"{options} exited with"

# negativ test - exit code 1: Allgemeiner Fehler
# Dieser Code wird verwendet, um anzuzeigen, dass ein nicht spezifizierter Fehler aufgetreten ist.
@pytest.mark.parametrize(
    "options",
    [
        ("--cm", "import", "-v", 'True'),
        ("--cd", "import", "-v", 'test.csv'),
        ("--cmd", "import", "-csv", "test_csv.csv", "-v", "alt"),    
    ],
)
#@pytest.mark.skip()
def test_cli_with_system_exit_code_2(options):
    runner = CliRunner()

    result = runner.invoke(cli.execute, options)

    assert result.exit_code == 2, f"{options} exited with"

# negativ test - exit code 2: Falsche Verwendung / Ungültige Argumente
# Dieser Code zeigt an, dass der Benutzer das Programm mit ungültigen Argumenten oder einer falschen Verwendung aufgerufen hat.
#@pytest.mark.skip()
@pytest.mark.parametrize(
    "options",
    [
        ("--cm", "import", "-v", True),
        ("--cd", "import", "-v", False),
        ("--v", "import",), 
    ],
)
def test_cli_with_system_exit_code_2(options):
    runner = CliRunner()

    result = runner.invoke(cli.execute, options)

    assert result.exit_code == 2, f"{options} exited with"
