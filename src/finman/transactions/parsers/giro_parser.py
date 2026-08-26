import csv
import logging
from datetime import datetime
from decimal import Decimal

from .base_parser import BaseCSVParser, TransactionData, parse_german_number

logger = logging.getLogger(__name__)


class GiroDKBCSVParser(BaseCSVParser):
    """Parser for DKB Girokonto CSV exports.

    Format:
    - Lines 1-3: Meta information (Girokonto/IBAN, Zeitraum, Kontostand)
    - Line 4: Empty separator line
    - Line 5: Header
    - Lines 6+: Data rows

    Header columns:
    Buchungsdatum;Wertstellung;Status;Zahlungspflichtige*r;Zahlungsempfänger*in;
    Verwendungszweck;Umsatztyp;IBAN;Betrag (€);Gläubiger-ID;Mandatsreferenz;Kundenreferenz

    The debitor depends on Umsatztyp:
    - "Eingang" → Zahlungspflichtige*r
    - "Ausgang" → Zahlungsempfänger*in
    """

    DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y']
    ENCODING = 'utf-8-sig'

    @staticmethod
    def parse_date(date_str: str):
        date_str = date_str.strip()
        for fmt in GiroDKBCSVParser.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def detect(self, filepath: str) -> bool:
        logger.info(f'GiroDKBCSVParser.detect: Checking {filepath}')
        try:
            with open(filepath, 'r', encoding=self.ENCODING) as f:
                first_line = f.readline().strip().replace('"', '')
                logger.info(f'GiroDKBCSVParser.detect: First line: {repr(first_line)}')
                result = first_line.startswith('Girokonto;')
                logger.info(f'GiroDKBCSVParser.detect: Match = {result}')
                return result
        except Exception as e:
            logger.warning(f'GiroDKBCSVParser.detect: Exception: {e}')
            return False

    def get_meta_info(self, filepath: str) -> dict:
        logger.info(f'GiroDKBCSVParser.get_meta_info: Reading {filepath}')
        try:
            with open(filepath, 'r', encoding=self.ENCODING) as f:
                first_line = f.readline().strip().replace('"', '')
                parts = first_line.split(';')
                konto = parts[1] if len(parts) > 1 else ''
                logger.info(f'GiroDKBCSVParser.get_meta_info: Konto = {konto}')

                header_found = False
                preview_rows = []
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if row and row[0] == 'Buchungsdatum':
                        header_found = True
                        continue
                    if header_found and row[0]:
                        preview_rows.append(row)
                        if len(preview_rows) >= 3:
                            break

                logger.info(f'GiroDKBCSVParser.get_meta_info: Preview rows = {len(preview_rows)}')
                return {
                    'konto': konto,
                    'parser_name': 'GiroDKBCSVParser',
                    'preview_rows': preview_rows[:3],
                }
        except Exception as e:
            logger.warning(f'GiroDKBCSVParser.get_meta_info: Exception: {e}')
            return {}

    def parse(self, filepath: str) -> list[TransactionData]:
        logger.info(f'GiroDKBCSVParser.parse: Starting to parse {filepath}')
        transactions = []
        skipped = 0

        with open(filepath, 'r', encoding=self.ENCODING) as f:
            first_line = f.readline().strip().replace('"', '')
            parts = first_line.split(';')
            src_konto = parts[1] if len(parts) > 1 else ''
            logger.info(f'GiroDKBCSVParser.parse: src_konto = {src_konto}')

            reader = csv.reader(f, delimiter=';')
            header_found = False
            col_map = {}

            for row in reader:
                if not header_found:
                    if row and row[0] == 'Buchungsdatum':
                        header_found = True
                        for i, col in enumerate(row):
                            col_map[col.strip()] = i
                        logger.info(f'GiroDKBCSVParser.parse: Header found, columns = {list(col_map.keys())}')
                    continue

                if not row or not row[0].strip():
                    continue

                try:
                    date_str = row[col_map['Buchungsdatum']].strip()
                    tx_date = self.parse_date(date_str)
                    if tx_date is None:
                        skipped += 1
                        logger.warning(f'GiroDKBCSVParser.parse: Skipping row, invalid date: {date_str}, row = {row}')
                        continue

                    status = row[col_map.get('Status', 2)].strip()
                    umsatztyp = row[col_map.get('Umsatztyp', 6)].strip()
                    logger.debug(f'GiroDKBCSVParser.parse: Umsatztyp = {umsatztyp}')

                    zahlungspflichtiger = ''
                    zahlungsempfaenger = ''
                    if 'Zahlungspflichtige*r' in col_map:
                        zahlungspflichtiger = row[col_map['Zahlungspflichtige*r']].strip()
                    if 'Zahlungsempfänger*in' in col_map:
                        zahlungsempfaenger = row[col_map['Zahlungsempfänger*in']].strip()

                    if umsatztyp == 'Eingang':
                        debitor = zahlungspflichtiger
                        logger.debug(f'GiroDKBCSVParser.parse: Debitor from Zahlungspflichtige*r = {debitor}')
                    else:
                        debitor = zahlungsempfaenger
                        logger.debug(f'GiroDKBCSVParser.parse: Debitor from Zahlungsempfänger*in = {debitor}')

                    verwendung = ''
                    if 'Verwendungszweck' in col_map:
                        verwendung = row[col_map['Verwendungszweck']].strip()

                    target_konto = ''
                    if 'IBAN' in col_map:
                        target_konto = row[col_map['IBAN']].strip()

                    betrag_str = ''
                    if 'Betrag (€)' in col_map:
                        betrag_str = row[col_map['Betrag (€)']].strip()
                    value = parse_german_number(betrag_str)
                    logger.debug(f'GiroDKBCSVParser.parse: Value = {value}')

                    debitor_id = ''
                    if 'Gläubiger-ID' in col_map:
                        debitor_id = row[col_map['Gläubiger-ID']].strip()

                    mandats_ref = ''
                    if 'Mandatsreferenz' in col_map:
                        mandats_ref = row[col_map['Mandatsreferenz']].strip()

                    customer_ref = ''
                    if 'Kundenreferenz' in col_map:
                        customer_ref = row[col_map['Kundenreferenz']].strip()

                    td = TransactionData(
                        date=tx_date,
                        value=value,
                        debitor=debitor,
                        src_konto=src_konto,
                        status=status,
                        verwendung=verwendung,
                        target_konto=target_konto,
                        debitor_id=debitor_id,
                        mandats_ref=mandats_ref,
                        customer_ref=customer_ref,
                    )
                    transactions.append(td)
                except (ValueError, IndexError, KeyError) as e:
                    skipped += 1
                    logger.warning(f'GiroDKBCSVParser.parse: Skipping row: {e}, row = {row}')
                    continue

        logger.info(f'GiroDKBCSVParser.parse: Completed. {len(transactions)} transactions, {skipped} skipped')
        return transactions
