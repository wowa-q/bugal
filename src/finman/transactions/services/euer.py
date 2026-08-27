from decimal import Decimal, ROUND_HALF_UP

from ..models import EuerPosition


INTERVALL_TO_ANNUAL_FACTOR = {
    'wöchentlich': Decimal('52'),
    'monatlich': Decimal('12'),
    'quartal': Decimal('4'),
    'halbjährlich': Decimal('2'),
    'jährlich': Decimal('1'),
    'einmalig': Decimal('1'),
    'geplant': Decimal('1'),
    'abgelaufen': Decimal('1'),
    '': Decimal('1'),
}

TARGET_DIVISOR = {
    'täglich': Decimal('365.25'),
    'wöchentlich': Decimal('52'),
    'monatlich': Decimal('12'),
    'jährlich': Decimal('1'),
}


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def normalize_amount(amount: Decimal, intervall: str, target: str) -> Decimal:
    if intervall == 'abgelaufen':
        return _quantize(amount)
    annual = amount * INTERVALL_TO_ANNUAL_FACTOR.get(intervall or 'jährlich', Decimal('1'))
    divisor = TARGET_DIVISOR[target]
    return _quantize(annual / divisor)


def _tx_category_path(tx) -> str:
    cats = list(tx.categories.select_related('category').all())
    if not cats:
        return ''
    return cats[0].category.get_full_path()


def position_summary(position: EuerPosition) -> dict:
    txs = list(position.transactions.select_related().all())
    if not txs:
        cat = position.category
        if cat and cat.parent:
            kategorie = cat.parent.name
            sub_kategorie = cat.name
        elif cat:
            kategorie = cat.name
            sub_kategorie = ''
        else:
            kategorie = ''
            sub_kategorie = ''
        betrag = Decimal('0.00')
        intervall = position.intervall or ''
        return {
            'betrag': _quantize(betrag),
            'kategorie': kategorie,
            'sub_kategorie': sub_kategorie,
            'typ': position.art or '',
            'intervall': intervall,
            'prioritaet': position.prioritaet or '',
            'konto': '',
            'täglich': Decimal('0.00'),
            'wöchentlich': Decimal('0.00'),
            'monatlich': Decimal('0.00'),
            'jährlich': Decimal('0.00'),
            'warnings': [],
            'has_warning': False,
        }

    betrag = sum((tx.value for tx in txs), Decimal('0'))

    cat = position.category
    if cat and cat.parent:
        kategorie = cat.parent.name
        sub_kategorie = cat.name
    elif cat:
        kategorie = cat.name
        sub_kategorie = ''
    else:
        kategorie = ''
        sub_kategorie = ''

    typ = position.art or ''
    intervall = position.intervall or ''
    prioritaet = position.prioritaet or ''

    first = sorted(txs, key=lambda t: t.date)[0]
    konto = first.src_konto or ''

    warnings = []
    pos_cat_path = cat.get_full_path() if cat else ''
    for tx in txs:
        tx_cat_path = _tx_category_path(tx)
        if tx_cat_path and pos_cat_path and tx_cat_path != pos_cat_path:
            if 'kategorie' not in warnings:
                warnings.append('kategorie')
        m = getattr(tx, 'meta', None)
        if m:
            if m.art and typ and m.art != typ and 'typ' not in warnings:
                warnings.append('typ')
            if m.intervall and intervall and m.intervall != intervall and 'intervall' not in warnings:
                warnings.append('intervall')
            if m.prioritaet and prioritaet and m.prioritaet != prioritaet and 'prioritaet' not in warnings:
                warnings.append('prioritaet')

    src_kontos = {tx.src_konto for tx in txs}
    if len(src_kontos) > 1:
        warnings.append('konto')

    if intervall == 'abgelaufen':
        täglich = _quantize(betrag)
        wöchentlich = _quantize(betrag)
        monatlich = _quantize(betrag)
        jährlich = _quantize(betrag)
    else:
        täglich = normalize_amount(betrag, intervall, 'täglich')
        wöchentlich = normalize_amount(betrag, intervall, 'wöchentlich')
        monatlich = normalize_amount(betrag, intervall, 'monatlich')
        jährlich = normalize_amount(betrag, intervall, 'jährlich')

    return {
        'betrag': _quantize(betrag),
        'kategorie': kategorie,
        'sub_kategorie': sub_kategorie,
        'typ': typ,
        'intervall': intervall,
        'prioritaet': prioritaet,
        'konto': konto,
        'täglich': täglich,
        'wöchentlich': wöchentlich,
        'monatlich': monatlich,
        'jährlich': jährlich,
        'warnings': warnings,
        'has_warning': bool(warnings),
    }
