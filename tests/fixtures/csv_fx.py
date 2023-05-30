# pylint: skip-file
# flake8: noqa

"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
from datetime import datetime

# 3rd party
import pytest
# from openpyxl import Workbook

# user packages
from context import bugal
from bugal import model
from bugal import cfg

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve()

@pytest.fixture
def fx_single_csv():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single.csv', 'w') as f:
        f.write('"Kontonummer:";"DE12345300001019363165 / Girokonto";\n')
        f.write('\n')
        f.write('"Von:";"31.12.2022";\n')
        f.write('"Bis:";"24.01.2023";\n')
        f.write('"Kontostand vom 24.01.2023:";"-1.835,87 EUR";\n')
        f.write('\n')
        f.write('"Buchungstag";"Wertstellung";"Buchungstext";"Auftraggeber / Begünstigter";"Verwendungszweck";"Kontonummer";"BLZ";"Betrag (EUR)";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz";\n')
        f.write('"24.01.2023";"24.01.2023";"FOLGELASTSCHRIFT";"PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV";"LU89751000135104200E";"PPLXLUL2";"-41,00";"LU96ZZZ0000000000000000058";"";"1024853056047";\n')
        f.write('"24.01.2023";"24.01.2023";"FOLGELASTSCHRIFT";"PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV";"LU89751000135104200E";"PPLXLUL2";"-41,00";"LU96ZZZ0000000000000000058";"";"1024853056047";\n')
        f.write('"23.01.2023";"23.01.2023";"Kartenzahlung/-abrechnung";"Eiscafe + Pizzeria Roni//Braunschweig/DE / Eiscafe + Pizzeria Roni";"2023-01-20T18:24      Debitk.1 2026-12";"DE86300500000001052141";"WELADEDDXXX";"-90,00";"";"";"61475723026701200123182418";\n')
        f.write('"23.01.2023";"23.01.2023";"Kartenzahlung";"ALDI SAGT DANKE";"2023-01-21      Debitk.14 VISA Debit";"DE96120300009005290904";"BYLADEM1001";"-83,99";"";"";"483021509531576";\n')
        f.write('"16.01.2023";"16.01.2023";"Kartenzahlung/-abrechnung";"ROSSMANN//Braunschweig/DE / ROSSMANN";"2023-01-13T17:52      Debitk.1 2026-12";"DE81300500000001078518";"WELADEDDXXX";"-54,41";"";"";"60304412024293130123175213";\n')
        pth = FIXTURE_DIR / 'single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_banch_of_csv(fx_single_csv):
    pth = FIXTURE_DIR / 'csv'
    try:
        pth.mkdir()
        for n in range(3):
            name = 'single_'+str(n)+'.csv'
            shutil.copy(fx_single_csv, pth / name)
            # with open(pth / name, 'w') as f:
            #     f.write('a;b;c')
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
def fx_single_invalid_csv():
    pth = ''
    with open(FIXTURE_DIR / 'single.csv', 'w') as f:
        f.write('a;b;c')
        pth = FIXTURE_DIR / 'single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_banch_of_invalid_csv(fx_single_csv):
    pth = FIXTURE_DIR / 'csv'
    try:
        pth.mkdir()
        for n in range(3):
            name = 'single_'+str(n)+'.csv'            
            with open(pth / name, 'w') as f:
                f.write('a;b;c')
        shutil.copy(fx_single_csv, pth / 'valid.csv')
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
def fx_zip_archive():
    zip_file = FIXTURE_DIR.parent.parent.resolve() / 'bugal_p' / 'archive.zip'

    yield zip_file

    try:
        zip_file.unlink()
    except PermissionError:
        pass