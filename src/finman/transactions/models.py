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


class EuerPosition(models.Model):
    name = models.CharField(max_length=100)
    hint = models.TextField(blank=True, default='')
    year = models.IntegerField()
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='euer_positions',
    )
    art = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)
    intervall = models.CharField(max_length=20, choices=INTERVALL_CHOICES, blank=True)
    prioritaet = models.CharField(
        max_length=20, choices=PRIORITAET_CHOICES, blank=True
    )
    transactions = models.ManyToManyField(
        'Transaction',
        related_name='euer_positions',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [('name', 'year')]
        verbose_name = 'EÜR-Position'
        verbose_name_plural = 'EÜR-Positionen'

    def __str__(self):
        return f"{self.name} ({self.year})"


GEBRAUCHTKAUF_CHOICES = [
    ('ja', 'Ja'),
    ('nein', 'Nein'),
]

ENTSCHEIDUNG_CHOICES = [
    ('geplant', 'Geplant'),
    ('geprueft', 'Geprüft'),
    ('genehmigt', 'Genehmigt'),
    ('abgelehnt', 'Abgelehnt'),
    ('verschoben', 'Verschoben'),
    ('umgesetzt', 'Umgesetzt'),
]


class PlannedInvestment(models.Model):
    investitionsobjekt = models.CharField(max_length=200)
    datum = models.DateField(null=True, blank=True)
    kategorie = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='investments')
    prioritaet = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, blank=True)
    nutzniesser = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, blank=True, verbose_name='Wem nützt es?')
    roi = models.TextField(blank=True, verbose_name='ROI')
    aktuelle_loesung = models.TextField(blank=True)
    nutzung_ab = models.DateField(null=True, blank=True, verbose_name='Ab wann soll es genutzt werden?')
    intervall = models.CharField(max_length=20, choices=INTERVALL_CHOICES, blank=True, verbose_name='Wie oft wird es genutzt')
    zeitaufwand_min = models.DurationField(null=True, blank=True, verbose_name='Zeitaufwand je Nutzung min')
    zeitaufwand_max = models.DurationField(null=True, blank=True, verbose_name='Zeitaufwand je Nutzung max')
    nutzungsdauer_min = models.CharField(max_length=100, blank=True, verbose_name='Wie lange genutzt min')
    nutzungsdauer_max = models.CharField(max_length=100, blank=True, verbose_name='Wie lange genutzt max')
    diy_workaround = models.TextField(blank=True, verbose_name='DIY Workaround')
    gebrauchtkauf_status = models.CharField(max_length=10, choices=GEBRAUCHTKAUF_CHOICES, blank=True, verbose_name='Gebrauchtkauf')
    gebrauchtkauf_begruendung = models.TextField(blank=True)
    mietmoeglichkeit = models.TextField(blank=True, verbose_name='Mietmöglichkeit')
    preis_entwicklung = models.CharField(max_length=200, blank=True, verbose_name='voraussichtliche Preisentwicklung')
    folgeanschaffungen = models.TextField(blank=True, verbose_name='Folgeanschaffungen')

    # Kosten min/max EUR
    mietkosten_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    mietkosten_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    anschaffungspreis_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    anschaffungspreis_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    folgeanschaffungen_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    folgeanschaffungen_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    inbetriebnahme_kosten_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Inbetriebnahme Kosten min')
    inbetriebnahme_kosten_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Inbetriebnahme Kosten max')
    inbetriebnahme_zeit_min = models.DurationField(null=True, blank=True, verbose_name='Inbetriebnahme Zeit min')
    inbetriebnahme_zeit_max = models.DurationField(null=True, blank=True, verbose_name='Inbetriebnahme Zeit max')
    betriebskosten_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    betriebskosten_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    instandhaltung_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Instandhaltungskosten min')
    instandhaltung_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Instandhaltungskosten max')
    reinigung_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Reinigung min')
    reinigung_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Reinigung max')
    versicherung_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Versicherung min')
    versicherung_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Versicherung max')
    reparatur_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Reparatur min')
    reparatur_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Reparatur max')
    entsorgung_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Entsorgung min')
    entsorgung_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Entsorgung max')

    wiederverkauf_prozent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Wiederverkauf % vom Anschaffungspreis')
    letzte_ueberpruefung = models.DateField(null=True, blank=True, verbose_name='letzte Überprüfung dieser Angaben')

    euer_position = models.OneToOneField(EuerPosition, null=True, blank=True, on_delete=models.SET_NULL, related_name='investment')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datum', 'investitionsobjekt']
        verbose_name = 'Geplantes Investment'
        verbose_name_plural = 'Geplante Investments'

    def __str__(self):
        return self.investitionsobjekt

    def _avg(self, min_val, max_val):
        if min_val is None and max_val is None:
            return None
        if max_val is None or max_val == '':
            return min_val
        if min_val is None or min_val == '':
            return max_val
        return (min_val + max_val) / 2

    @property
    def mietkosten_avg(self):
        return self._avg(self.mietkosten_min, self.mietkosten_max)

    @property
    def anschaffungspreis_avg(self):
        return self._avg(self.anschaffungspreis_min, self.anschaffungspreis_max)

    @property
    def folgeanschaffungen_avg(self):
        return self._avg(self.folgeanschaffungen_min, self.folgeanschaffungen_max)

    @property
    def inbetriebnahme_kosten_avg(self):
        return self._avg(self.inbetriebnahme_kosten_min, self.inbetriebnahme_kosten_max)

    @property
    def betriebskosten_avg(self):
        return self._avg(self.betriebskosten_min, self.betriebskosten_max)

    @property
    def instandhaltung_avg(self):
        return self._avg(self.instandhaltung_min, self.instandhaltung_max)

    @property
    def reinigung_avg(self):
        return self._avg(self.reinigung_min, self.reinigung_max)

    @property
    def versicherung_avg(self):
        return self._avg(self.versicherung_min, self.versicherung_max)

    @property
    def reparatur_avg(self):
        return self._avg(self.reparatur_min, self.reparatur_max)

    @property
    def entsorgung_avg(self):
        return self._avg(self.entsorgung_min, self.entsorgung_max)

    @property
    def wiederverkauf_betrag(self):
        avg = self.anschaffungspreis_avg
        if avg is None or self.wiederverkauf_prozent is None:
            return None
        return avg * self.wiederverkauf_prozent / 100

    @property
    def gesamt_min(self):
        vals = [self.mietkosten_min, self.anschaffungspreis_min, self.folgeanschaffungen_min, self.inbetriebnahme_kosten_min, self.betriebskosten_min, self.instandhaltung_min, self.reinigung_min, self.versicherung_min, self.reparatur_min, self.entsorgung_min]
        vals = [v for v in vals if v is not None]
        return sum(vals, 0) if vals else None

    @property
    def gesamt_max(self):
        vals = [self.mietkosten_max if self.mietkosten_max is not None else self.mietkosten_min, self.anschaffungspreis_max if self.anschaffungspreis_max is not None else self.anschaffungspreis_min, self.folgeanschaffungen_max if self.folgeanschaffungen_max is not None else self.folgeanschaffungen_min, self.inbetriebnahme_kosten_max if self.inbetriebnahme_kosten_max is not None else self.inbetriebnahme_kosten_min, self.betriebskosten_max if self.betriebskosten_max is not None else self.betriebskosten_min, self.instandhaltung_max if self.instandhaltung_max is not None else self.instandhaltung_min, self.reinigung_max if self.reinigung_max is not None else self.reinigung_min, self.versicherung_max if self.versicherung_max is not None else self.versicherung_min, self.reparatur_max if self.reparatur_max is not None else self.reparatur_min, self.entsorgung_max if self.entsorgung_max is not None else self.entsorgung_min]
        vals = [v for v in vals if v is not None]
        return sum(vals, 0) if vals else None

    @property
    def gesamt_avg(self):
        return self._avg(self.gesamt_min, self.gesamt_max)


class InvestmentDecision(models.Model):
    investment = models.ForeignKey(PlannedInvestment, on_delete=models.CASCADE, related_name='entscheidungen')
    status = models.CharField(max_length=20, choices=ENTSCHEIDUNG_CHOICES, default='geplant')
    datum = models.DateField(null=True, blank=True)
    begruendung = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-datum', '-created_at']
        verbose_name = 'Investmententscheidung'
        verbose_name_plural = 'Investmententscheidungen'

    def __str__(self):
        return f"{self.investment.investitionsobjekt} - {self.get_status_display()}"


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
