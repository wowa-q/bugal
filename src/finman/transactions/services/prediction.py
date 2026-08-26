from datetime import timedelta
from statistics import mean, stdev

from django.db.models import Count

from ..models import Transaction, TransactionCategory, PredictionResult, Category


def update_predictions():
    predictions = {}

    for tx in Transaction.objects.order_by('debitor', 'date'):
        key = (tx.debitor, None)
        if key not in predictions:
            predictions[key] = []
        predictions[key].append(tx.date)

    for tx in Transaction.objects.order_by('date'):
        cats = tx.categories.select_related('category').all()
        for tc in cats:
            key = (tx.debitor, tc.category.pk)
            if key not in predictions:
                predictions[key] = []
            predictions[key].append(tx.date)

    for (debitor, cat_id), dates in predictions.items():
        if len(dates) < 2:
            continue
        dates = sorted(set(dates))
        diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        if not diffs:
            continue

        avg = mean(diffs)
        std = stdev(diffs) if len(diffs) > 1 else 0
        confidence = max(0.0, 1.0 - (std / avg)) if avg > 0 else 0.0

        category = None
        if cat_id is not None:
            category = Category.objects.get(pk=cat_id)

        PredictionResult.objects.update_or_create(
            debitor=debitor,
            category=category,
            defaults={
                'next_expected_date': dates[-1] + timedelta(days=int(avg)),
                'avg_interval_days': int(avg),
                'last_occurrence': dates[-1],
                'confidence': round(confidence, 2),
            },
        )
