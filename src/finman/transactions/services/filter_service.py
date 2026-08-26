from datetime import date

from ..models import Transaction, TransactionCategory, TransactionMeta, Category


class TransactionFilter:

    def __init__(self):
        self.qs = Transaction.objects.all()

    def by_date_range(self, start: date, end: date):
        self.qs = self.qs.filter(date__range=(start, end))
        return self

    def by_debitor(self, name: str):
        if name:
            self.qs = self.qs.filter(debitor__icontains=name)
        return self

    def by_category(self, category_id: int):
        if category_id:
            cat = Category.objects.get(pk=category_id)
            cat_ids = cat.get_descendants()
            self.qs = self.qs.filter(categories__category__in=cat_ids)
        return self

    def by_art(self, art: str):
        if art:
            self.qs = self.qs.filter(meta__art=art)
        return self

    def by_prioritaet(self, prio: str):
        if prio:
            self.qs = self.qs.filter(meta__prioritaet=prio)
        return self

    def by_intervall(self, intervall: str):
        if intervall:
            self.qs = self.qs.filter(meta__intervall=intervall)
        return self

    def apply(self):
        return self.qs.distinct()
