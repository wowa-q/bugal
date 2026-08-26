import csv
import logging
from datetime import datetime
from decimal import Decimal

from .base_parser import BaseCSVParser, TransactionData, parse_german_number

logger = logging.getLogger(__name__)


class GenericCSVParser(BaseCSVParser):
    """Fallback parser that treats the first non-empty line as header.

    Provides a column mapping interface for manual field assignment.
    """

    DATE_FORMATS = ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d', '%m/%d/%Y']

    TARGET_FIELDS = [
        'date', 'value', 'debitor', 'src_konto', 'status',
        'verwendung', 'target_konto', 'debitor_id', 'mandats_ref', 'customer_ref',
    ]

    def detect(self, filepath: str) -> bool:
        logger.info(f'GenericCSVParser.detect: Acting as fallback for {filepath}')
        return True

    def get_meta_info(self, filepath: str) -> dict:
        logger.info(f'GenericCSVParser.get_meta_info: Reading {filepath}')
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                if ',' in f.readline():
                    delimiter = ','
                else:
                    delimiter = ';'
                logger.info(f'GenericCSVParser.get_meta_info: Delimiter = {repr(delimiter)}')
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=delimiter)
                for row in reader:
                    if row:
                        logger.info(f'GenericCSVParser.get_meta_info: Header = {row}')
                        return {
                            'konto': '',
                            'parser_name': 'GenericCSVParser',
                            'preview_rows': [row] + [next(reader, []) for _ in range(2)],
                            'headers': row,
                        }
        except Exception as e:
            logger.warning(f'GenericCSVParser.get_meta_info: Exception: {e}')
        return {}

    def parse(self, filepath: str, column_mapping: dict | None = None) -> list[TransactionData]:
        logger.info(f'GenericCSVParser.parse: Starting to parse {filepath}, mapping = {column_mapping}')
        transactions = []
        skipped = 0

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            delimiter = ';' if ';' in first_line else ','
            logger.info(f'GenericCSVParser.parse: Delimiter = {repr(delimiter)}')

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            logger.info(f'GenericCSVParser.parse: DictReader fields = {reader.fieldnames}')

            for row in reader:
                try:
                    date_str = self._get_field(row, column_mapping, 'date')
                    tx_date = self._parse_date(date_str)
                    if tx_date is None:
                        logger.debug(f'GenericCSVParser.parse: Skipping row, no valid date: {date_str}')
                        skipped += 1
                        continue

                    value_str = self._get_field(row, column_mapping, 'value')
                    value = parse_german_number(value_str) if value_str else Decimal('0')

                    debitor = self._get_field(row, column_mapping, 'debitor') or ''

                    td = TransactionData(
                        date=tx_date,
                        value=value,
                        debitor=debitor,
                        src_konto=self._get_field(row, column_mapping, 'src_konto') or '',
                        status=self._get_field(row, column_mapping, 'status') or '',
                        verwendung=self._get_field(row, column_mapping, 'verwendung') or '',
                        target_konto=self._get_field(row, column_mapping, 'target_konto') or '',
                        debitor_id=self._get_field(row, column_mapping, 'debitor_id') or '',
                        mandats_ref=self._get_field(row, column_mapping, 'mandats_ref') or '',
                        customer_ref=self._get_field(row, column_mapping, 'customer_ref') or '',
                    )
                    transactions.append(td)
                except (ValueError, KeyError) as e:
                    skipped += 1
                    logger.warning(f'GenericCSVParser.parse: Skipping row: {e}, row = {dict(row)}')
                    continue

        logger.info(f'GenericCSVParser.parse: Completed. {len(transactions)} transactions, {skipped} skipped')
        return transactions

    def _get_field(self, row: dict, mapping: dict | None, field_name: str) -> str | None:
        if mapping and field_name in mapping and mapping[field_name]:
            return row.get(mapping[field_name], '').strip()
        return row.get(field_name, '').strip()

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
