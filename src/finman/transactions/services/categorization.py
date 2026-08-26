from ..models import Transaction, TransactionCategory, TransactionMeta, FilterRule


def _first_matching_rule(transaction: Transaction, rules) -> FilterRule | None:
    for rule in rules:
        debitor_match = (
            not rule.debitor_contains or
            rule.debitor_contains.lower() in transaction.debitor.lower()
        )
        verwendung_match = (
            not rule.verwendung_contains or
            rule.verwendung_contains.lower() in transaction.verwendung.lower()
        )
        if debitor_match and verwendung_match:
            return rule
    return None


def match_rule(transaction: Transaction) -> FilterRule | None:
    """Returns the first active FilterRule matching the transaction, or None."""
    rules = FilterRule.objects.filter(is_active=True).select_related('category')
    return _first_matching_rule(transaction, rules)


def _assign_rule(transaction: Transaction, rule: FilterRule) -> None:
    if rule.category_id:
        TransactionCategory.objects.get_or_create(
            transaction=transaction,
            category=rule.category,
            defaults={'assigned_by': 'auto'},
        )
    TransactionMeta.objects.update_or_create(
        transaction=transaction,
        defaults={
            'rule': rule,
            'art': rule.art,
            'prioritaet': rule.prioritaet,
            'intervall': rule.intervall,
        },
    )


def auto_categorize(transaction: Transaction) -> None:
    rule = match_rule(transaction)
    if rule:
        _assign_rule(transaction, rule)


def apply_rules_to_all() -> dict:
    """Re-applies active rules to every stored transaction.

    Deletes all automatically assigned categories and rule metadata first,
    then rebuilds them from the currently active rules. Manual assignments
    (assigned_by='manual') are never touched.

    NOTE: TransactionMeta rows are only ever written by auto_categorize,
    so deleting them all is safe today. Revisit if manual meta is introduced.
    """
    TransactionCategory.objects.filter(assigned_by='auto').delete()
    TransactionMeta.objects.all().delete()

    rules = FilterRule.objects.filter(is_active=True).select_related('category')
    processed = 0
    matched = 0
    unmatched = 0

    for tx in Transaction.objects.iterator():
        processed += 1
        rule = _first_matching_rule(tx, rules)
        if rule:
            _assign_rule(tx, rule)
            matched += 1
        else:
            unmatched += 1

    return {'processed': processed, 'matched': matched, 'unmatched': unmatched}
