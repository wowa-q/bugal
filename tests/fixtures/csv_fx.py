# pylint: skip-file
# flake8: noqa

"""The module shall hold the fixtures, which can be used in the test"""


import pathlib
import shutil
import random
import time
import zipfile
from datetime import datetime

# 3rd party
import pytest
# from openpyxl import Workbook

# user packages
from context import bugal
from bugal.app import model
from bugal.cfg import cfg as tom

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
        f.write('"24.01.2023";"24.01.2023";"Classic";"PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV";"LU89751000135104200E";"PPLXLUL2";"-51,00";"LU96ZZZ0000000000000000058";"";"1024853056047";\n')
        f.write('"24.01.2023";"24.02.2023";"Classic";"PayPal Europe S.a.r.l. et Cie S.C.A";"1024853056047 . Canon Europa NV, Ihr Einkauf bei Canon Europa NV";"LU89751000135104200E";"PPLXLUL2";"-41,00";"LU96ZZZ0000000000000000058";"";"1024853056047";\n')
        f.write('"16.01.2023";"23.03.2023";"Classic";"Eiscafe + Pizzeria Roni//Braunschweig/DE / Eiscafe + Pizzeria Roni";"2023-01-20T18:24      Debitk.1 2026-12";"DE86300500000001052141";"WELADEDDXXX";"-90,00";"";"";"61475723026701200123182418";\n')
        f.write('"23.01.2023";"23.04.2023";"Classic";"ALDI SAGT DANKE";"2023-01-21      Debitk.14 VISA Debit";"DE96120300009005290904";"BYLADEM1001";"-83,99";"";"";"483021509531576";\n')
        f.write('"16.01.2023";"16.05.2023";"Classic";"ROSSMANN//Braunschweig/DE / ROSSMANN";"2023-01-13T17:52      Debitk.1 2026-12";"DE81300500000001078518";"WELADEDDXXX";"-54,41";"";"";"60304412024293130123175213";\n')
        pth = FIXTURE_DIR / 'single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_single_csv_new():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single_new.csv', 'w') as f:

        f.write('"Konto";"Girokonto DE12345300001019363165";\n')
        f.write('"";\n')
        f.write('"Kontostand vom 20.10.2023:";"6,37 EUR";\n')
        f.write('"";\n')
        f.write('"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"Betrag";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz";\n')
        f.write('"19.10.23";"19.10.23";"Gebucht";"Angelina Merkel";"Angelina Merkel";"";"Ausgang";"-40,00 €";"";"";"";\n')
        f.write('"18.10.23";"18.10.23";"Gebucht";"Angelina Merkel";"Angelina Merkel";"";"Ausgang";"-100,00 €";"";"";"";\n')
        f.write('"17.10.23";"18.10.23";"Gebucht";"ISSUER";"Amazon.de/AMAZON.DE//LU";"2023-10-17 Debitk.17 VISA Debit";"Ausgang";"-39,61 €";"";"";"483287233545819";\n')
        f.write('"16.10.23";"17.10.23";"Gebucht";"Bundesagentur für Arbeit - Familienkasse";"Merkel, Angelina                                                      Bochumer Str. 17";"KG237007FK840606 1023 06054073515/3000170761965";"Eingang";"250,00 €";"";"";"06054073515";\n')
        f.write('"15.10.23";"17.10.23";"Gebucht";"Angelina Merkel                                                       Bochumerstr. 17";"PayPal Europe S.a.r.l. et Cie S.C.A";"1030022989820 . Gymondo GmbH, Ihr Einkauf bei Gymondo GmbH";"Ausgang";"-59,88 €";"LU96ZZZ0000000000000000058";"4NS2224N238BJ";"1030022989820";\n')
        f.write('"14.10.23";"17.10.23";"Gebucht";"ALTEN Technology GmbH                                                 Gasstr. 4";"Merkel Angelina                                                       NA";"Lohn-Gehalt Abrechnung 09/2023";"Eingang";"2.228,57 €";"";"";"032SALA019182";\n')
        
        pth = FIXTURE_DIR / 'single_new.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_single_csv_single_line():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single_new_single.csv', 'w') as f:
        f.write('"Konto";"Girokonto DE12345300001019363165";\n')
        f.write('\n')
        f.write('"Kontostand vom 08.06.2023:"; "-152,71 EUR";\n')
        f.write('\n')
        f.write('"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"Betrag";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz";\n')
        f.write('"24.01.2022";"24.01.2023";"Gebucht";"Hanse-Merkur";"KLOOS, WALDEMAR";"083257346A00016 07.06.2023- 1";"Eingang";"54,97 €";"";"";"21521570";\n')
    
    pth = FIXTURE_DIR / 'single_new_single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_csv_broken_date_classic():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single_new_single.csv', 'w') as f:
        f.write('Kontonummer:;DE12345300001019363165 / Girokonto;;;;;;;;;;\n')
        f.write(';;;;;;;;;;\n')
        f.write('Von:;31.12.2022;;;;;;;;;\n')
        f.write('Bis:;24.01.2023;;;;;;;;;\n')
        f.write('"Kontostand vom 08.06.2023:"; "-152,71 EUR";\n')
        f.write(';;;;;;;;;;\n')
        f.write('"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"Betrag";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz";\n')
        f.write('"1a.a1.23";"1a.10.23";"Gebucht";"Hanse-Merkur";"KLOOS, WALDEMAR";"083257346A00016 07.06.2023- 1";"Eingang";"54,97 €";"";"";"21521570";\n')
       
    pth = FIXTURE_DIR / 'single_new_single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_csv_broken_date_beta():
    """Definitiaon of csv file, which shall be created and deleted when the test was done

    Yields:
        path string: file path
    """
    pth = ''
    with open(FIXTURE_DIR / 'single_new.csv', 'w') as f:

        f.write('"Konto";"Girokonto DE12345300001019363165";\n')
        f.write('"";\n')
        f.write('"Kontostand vom 20.10.2023:";"6,37 EUR";\n')
        f.write('"";\n')
        f.write('"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"Betrag";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz";\n')
        f.write('"24.a1.2022";"1a1023";"Gebucht";"Angelina Merkel";"Angelina Merkel";"";"Ausgang";"-40,00 €";"";"";"";\n')
        
        pth = FIXTURE_DIR / 'single_new.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def fx_banch_of_csv(fx_single_csv):
    if fx_single_csv.exists():
        pth = FIXTURE_DIR / 'csv'
        try:
            pth.mkdir()
            for n in range(3):
                name = 'single_'+str(n)+'.csv'
                shutil.copy2(fx_single_csv, pth / name)
        except FileExistsError:
            pass  
    else:
        raise FileExistsError
    
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
    with open(FIXTURE_DIR / 'inv_single.csv', 'w') as f:
        f.write('a;b;c')
        pth = FIXTURE_DIR / 'inv_single.csv'

    yield pth 
    # delete the modified db file and copy one to make repeat of the test possible
    try:
        pth.unlink()
    except FileNotFoundError:
        pass 

@pytest.fixture
def fx_banch_of_invalid_csv(fx_single_csv):
    pth = FIXTURE_DIR / 'inv_csv'
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
    archive = FIXTURE_DIR.resolve() / 'archive.zip'
    with zipfile.ZipFile(FIXTURE_DIR.resolve() / 'archive.zip', 'w') as myzip:
        pass

    yield archive
        
    try:
        archive.unlink()
    except PermissionError:
        pass

@pytest.fixture
def fx_zip_archive_configured():
    config = tom.load_config()
    src_config = config['bugal']['src']
    for cfg in src_config:
        if pathlib.Path(cfg.get('zip_file')).is_file():
            archive = tom.ARCHIVE
        else:
            archive = pathlib.Path(cfg.get('zip_file'))
            with zipfile.ZipFile(archive, 'w') as myzip:
                pass

    yield archive
        
    # try:
    #     archive.unlink()
    # except PermissionError:
    #     pass