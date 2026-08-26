import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class TransactionData:
    date: date
    value: Decimal
    debitor: str
    src_konto: str
    status: str = ''
    verwendung: str = ''
    target_konto: str = ''
    debitor_id: str = ''
    mandats_ref: str = ''
    customer_ref: str = ''


class BaseCSVParser(ABC):

    @abstractmethod
    def detect(self, filepath: str) -> bool:
        """Returns True if this parser can handle the CSV file."""
        ...

    @abstractmethod
    def parse(self, filepath: str) -> list[TransactionData]:
        """Parses the CSV file and returns a list of TransactionData."""
        ...

    def get_meta_info(self, filepath: str) -> dict:
        """Returns metadata about the file (konto name, preview rows)."""
        return {}


def compute_transaction_hash(td: TransactionData) -> str:
    raw = f"{td.date}{td.debitor}{td.value}{td.verwendung}{td.target_konto}{td.src_konto}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def compute_file_md5(filepath: str) -> str:
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def parse_german_number(s: str) -> Decimal:
    s = s.strip().replace('\xa0', '').replace(' EUR', '').replace('€', '').strip()
    if s.startswith('-'):
        sign = -1
        s = s[1:]
    else:
        sign = 1
    s = s.replace('.', '').replace(',', '.')
    return Decimal(str(sign * float(s)))
