from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories',
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent__name', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def get_descendants(self):
        ids = [self.pk]
        for child in self.subcategories.all():
            ids.extend(child.get_descendants())
        return ids

    def get_full_path(self):
        names = []
        current = self
        while current is not None:
            names.append(current.name)
            current = current.parent
        return ' / '.join(reversed(names))


ASSIGNED_BY_CHOICES = [('auto', 'Automatisch'), ('manual', 'Manuell')]


class TransactionCategory(models.Model):
    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
        related_name='categories',
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_by = models.CharField(
        max_length=10,
        choices=ASSIGNED_BY_CHOICES,
        default='auto',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('transaction', 'category')]

    def __str__(self):
        return f"{self.transaction.debitor} -> {self.category}"


ART_CHOICES = [('FIX', 'Fix'), ('FLEX', 'Flex')]

PRIORITAET_CHOICES = [
    ('Familie', 'Familie'),
    ('Kinder', 'Kinder'),
    ('Waldemar', 'Waldemar'),
    ('Nastja', 'Nastja'),
    ('Uljana', 'Uljana'),
    ('Mischa', 'Mischa'),
]

INTERVALL_CHOICES = [
    ('einmalig', 'Einmalig'),
    ('wöchentlich', 'Wöchentlich'),
    ('monatlich', 'Monatlich'),
    ('quartal', 'Quartal'),
    ('halbjährlich', 'Halbjährlich'),
    ('jährlich', 'Jährlich'),
    ('abgelaufen', 'Abgelaufen'),
    ('geplant', 'Geplant'),
]


class FilterRule(models.Model):
    name = models.CharField(max_length=100)
    debitor_contains = models.CharField(max_length=255, blank=True)
    verwendung_contains = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    art = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)
    prioritaet = models.CharField(
        max_length=20,
        choices=PRIORITAET_CHOICES,
        blank=True,
    )
    intervall = models.CharField(
        max_length=20,
        choices=INTERVALL_CHOICES,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ImportHistory(models.Model):
    file_md5 = models.CharField(max_length=32, unique=True)
    filename = models.CharField(max_length=255)
    konto = models.CharField(max_length=100)
    imported_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    min_date = models.DateField(null=True, blank=True)
    max_date = models.DateField(null=True, blank=True)
    duplicate_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-imported_at']
        verbose_name = 'Import'
        verbose_name_plural = 'Importe'

    def __str__(self):
        return f"{self.filename} ({self.imported_at:%d.%m.%Y})"


class Transaction(models.Model):
    hash = models.CharField(max_length=64, unique=True)
    date = models.DateField()
    status = models.CharField(max_length=50, blank=True)
    debitor = models.CharField(max_length=255)
    verwendung = models.TextField(blank=True)
    target_konto = models.CharField(max_length=100, blank=True)
    src_konto = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    debitor_id = models.CharField(max_length=100, blank=True)
    mandats_ref = models.CharField(max_length=100, blank=True)
    customer_ref = models.CharField(max_length=100, blank=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    import_file = models.ForeignKey(
        ImportHistory,
        on_delete=models.CASCADE,
        null=True,
        related_name='transactions',
    )

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['debitor']),
            models.Index(fields=['value']),
        ]

    def __str__(self):
        return f"{self.date} | {self.debitor} | {self.value}"

    @property
    def attribute_count(self):
        count = self.categories.count()
        meta = getattr(self, 'meta', None)
        if meta:
            count += sum(1 for f in ('art', 'prioritaet', 'intervall') if getattr(meta, f))
        return count


class TransactionMeta(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='meta',
    )
    rule = models.ForeignKey(
        FilterRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    art = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)
    prioritaet = models.CharField(
        max_length=20,
        choices=PRIORITAET_CHOICES,
        blank=True,
    )
    intervall = models.CharField(
        max_length=20,
        choices=INTERVALL_CHOICES,
        blank=True,
    )

    def __str__(self):
        return f"Meta: {self.transaction.debitor}"


class TransactionInfo(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='info',
    )
    text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Info: {self.transaction.debitor}"


class PredictionResult(models.Model):
    debitor = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    next_expected_date = models.DateField()
    avg_interval_days = models.IntegerField()
    last_occurrence = models.DateField()
    confidence = models.FloatField()
    predicted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('debitor', 'category')]
        ordering = ['next_expected_date']

    def __str__(self):
        return f"{self.debitor} -> {self.next_expected_date}"
