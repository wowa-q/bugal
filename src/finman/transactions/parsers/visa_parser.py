import csv
import logging
from datetime import datetime
from decimal import Decimal

from .base_parser import BaseCSVParser, TransactionData, parse_german_number

logger = logging.getLogger(__name__)


class VisaDKBCSVParser(BaseCSVParser):
    """Parser for DKB Visa Kreditkarte CSV exports.

    Format:
    - Line 1: Karte;Visa Kreditkarte;4930 •••• •••• 0720
    - Line 2: Empty
    - Line 3: Saldo vom ...
    - Line 4: Empty
    - Line 5: Header
    - Lines 6+: Data rows

    Header columns:
    Belegdatum;Wertstellung;Status;Beschreibung;Umsatztyp;Betrag (€);Fremdwährungsbetrag
    """

    DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y']
    ENCODING = 'utf-8-sig'

    @staticmethod
    def parse_date(date_str: str):
        date_str = date_str.strip()
        for fmt in VisaDKBCSVParser.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def detect(self, filepath: str) -> bool:
        logger.info(f'VisaDKBCSVParser.detect: Checking {filepath}')
        try:
            with open(filepath, 'r', encoding=self.ENCODING) as f:
                first_line = f.readline().strip().replace('"', '')
                logger.info(f'VisaDKBCSVParser.detect: First line: {repr(first_line)}')
                result = first_line.startswith('Karte;')
                logger.info(f'VisaDKBCSVParser.detect: Match = {result}')
                return result
        except Exception as e:
            logger.warning(f'VisaDKBCSVParser.detect: Exception: {e}')
            return False

    def get_meta_info(self, filepath: str) -> dict:
        logger.info(f'VisaDKBCSVParser.get_meta_info: Reading {filepath}')
        try:
            with open(filepath, 'r', encoding=self.ENCODING) as f:
                first_line = f.readline().strip().replace('"', '')
                parts = first_line.split(';')
                konto = parts[2] if len(parts) > 2 else ''
                logger.info(f'VisaDKBCSVParser.get_meta_info: Konto = {konto}')

                header_found = False
                preview_rows = []
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if row and row[0] == 'Belegdatum':
                        header_found = True
                        continue
                    if header_found and row[0]:
                        preview_rows.append(row)
                        if len(preview_rows) >= 3:
                            break

                logger.info(f'VisaDKBCSVParser.get_meta_info: Preview rows = {len(preview_rows)}')
                return {
                    'konto': konto,
                    'parser_name': 'VisaDKBCSVParser',
                    'preview_rows': preview_rows[:3],
                }
        except Exception as e:
            logger.warning(f'VisaDKBCSVParser.get_meta_info: Exception: {e}')
            return {}

    def parse(self, filepath: str) -> list[TransactionData]:
        logger.info(f'VisaDKBCSVParser.parse: Starting to parse {filepath}')
        transactions = []
        skipped = 0

        with open(filepath, 'r', encoding=self.ENCODING) as f:
            first_line = f.readline().strip().replace('"', '')
            parts = first_line.split(';')
            src_konto = parts[2] if len(parts) > 2 else ''
            logger.info(f'VisaDKBCSVParser.parse: src_konto = {src_konto}')

            reader = csv.reader(f, delimiter=';')
            header_found = False
            col_map = {}

            for row in reader:
                if not header_found:
                    if row and row[0] == 'Belegdatum':
                        header_found = True
                        for i, col in enumerate(row):
                            col_map[col.strip()] = i
                        logger.info(f'VisaDKBCSVParser.parse: Header found, columns = {list(col_map.keys())}')
                    continue

                if not row or not row[0].strip():
                    continue

                try:
                    date_str = row[col_map['Belegdatum']].strip()
                    tx_date = self.parse_date(date_str)
                    if tx_date is None:
                        skipped += 1
                        logger.warning(f'VisaDKBCSVParser.parse: Skipping row, invalid date: {date_str}, row = {row}')
                        continue

                    status = row[col_map.get('Status', 2)].strip()
                    debitor = row[col_map.get('Beschreibung', 3)].strip()

                    umsatztyp = ''
                    if 'Umsatztyp' in col_map:
                        umsatztyp = row[col_map['Umsatztyp']].strip()

                    betrag_str = ''
                    if 'Betrag (€)' in col_map:
                        betrag_str = row[col_map['Betrag (€)']].strip()
                    value = parse_german_number(betrag_str)
                    logger.debug(f'VisaDKBCSVParser.parse: debitor = {debitor}, value = {value}')

                    td = TransactionData(
                        date=tx_date,
                        value=value,
                        debitor=debitor,
                        src_konto=src_konto,
                        status=status,
                        verwendung=umsatztyp,
                    )
                    transactions.append(td)
                except (ValueError, IndexError, KeyError) as e:
                    skipped += 1
                    logger.warning(f'VisaDKBCSVParser.parse: Skipping row: {e}, row = {row}')
                    continue

        logger.info(f'VisaDKBCSVParser.parse: Completed. {len(transactions)} transactions, {skipped} skipped')
        return transactions
