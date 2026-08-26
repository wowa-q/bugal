import logging
import os
import tempfile

from ..models import ImportHistory, Transaction
from ..parsers.base_parser import compute_file_md5, compute_transaction_hash
from ..parsers.registry import get_parser
from .categorization import auto_categorize

logger = logging.getLogger(__name__)


def save_upload_to_temp(uploaded_file) -> str:
    logger.info(f'save_upload_to_temp: Uploaded file: name={uploaded_file.name}, size={uploaded_file.size}, content_type={uploaded_file.content_type}')
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    for chunk in uploaded_file.chunks():
        tmp.write(chunk)
    tmp.close()
    logger.info(f'save_upload_to_temp: Saved to temp file: {tmp.name}')
    with open(tmp.name, 'rb') as f:
        first_bytes = f.read(100)
        logger.info(f'save_upload_to_temp: First 100 bytes (hex): {first_bytes.hex()}')
        logger.info(f'save_upload_to_temp: First 100 bytes (repr): {repr(first_bytes)}')
    return tmp.name


def cleanup_temp(filepath: str | None) -> None:
    if not filepath or not filepath.startswith(tempfile.gettempdir()):
        return
    try:
        os.unlink(filepath)
    except OSError:
        pass


def import_csv(filepath: str, original_filename: str | None = None) -> dict:
    logger.info(f'import_csv: Starting import of {filepath}')
    md5 = compute_file_md5(filepath)
    logger.info(f'import_csv: MD5 = {md5}')

    if ImportHistory.objects.filter(file_md5=md5).exists():
        existing = ImportHistory.objects.get(file_md5=md5)
        msg = f'Datei wurde bereits am {existing.imported_at:%d.%m.%Y %H:%M} importiert.'
        logger.warning(f'import_csv: Duplicate file detected. {msg}')
        raise ValueError(msg)

    logger.info(f'import_csv: Searching for parser...')
    parser = get_parser(filepath)
    if parser is None:
        logger.error(f'import_csv: No matching parser found')
        raise ValueError('Kein passender Parser fÃ¼r diese Datei gefunden.')

    logger.info(f'import_csv: Using parser {parser.__class__.__name__}')
    transactions_data = parser.parse(filepath)
    logger.info(f'import_csv: Parsed {len(transactions_data)} transactions from file')

    imported = 0
    skipped = 0

    import_history = ImportHistory(
        file_md5=md5,
        filename=original_filename or os.path.basename(filepath),
    )
    import_history.save()
    logger.info(f'import_csv: Created ImportHistory record with pk={import_history.pk}')

    for i, td in enumerate(transactions_data):
        tx_hash = compute_transaction_hash(td)
        if Transaction.objects.filter(hash=tx_hash).exists():
            skipped += 1
            logger.debug(f'import_csv: Skipping duplicate transaction {i+1}: {td.debitor[:40]}...')
            continue
        tx = Transaction(
            hash=tx_hash,
            date=td.date,
            value=td.value,
            debitor=td.debitor,
            src_konto=td.src_konto,
            status=td.status,
            verwendung=td.verwendung,
            target_konto=td.target_konto,
            debitor_id=td.debitor_id,
            mandats_ref=td.mandats_ref,
            customer_ref=td.customer_ref,
            import_file=import_history,
        )
        tx.save()
        logger.debug(f'import_csv: Saved transaction {i+1}: {td.debitor[:40]}... = {td.value}')

        auto_categorize(tx)
        imported += 1

    dates = [td.date for td in transactions_data]
    import_history.row_count = len(transactions_data)
    import_history.duplicate_count = skipped
    import_history.konto = transactions_data[0].src_konto if transactions_data else ''
    import_history.min_date = min(dates) if dates else None
    import_history.max_date = max(dates) if dates else None
    import_history.save()
    logger.info(f'import_csv: Updated ImportHistory: {imported} imported, {skipped} duplicates')

    result = {
        'imported': imported,
        'skipped': skipped,
        'duplicates': skipped,
        'import_id': import_history.pk,
    }
    logger.info(f'import_csv: Import complete. Result = {result}')
    return result
