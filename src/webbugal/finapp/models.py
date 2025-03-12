from tabnanny import verbose
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Create your models here.
META_TRANSACTION = {
    'tdate': '',
    'text': '',
    'status': '',
    'debitor': '',
    'verwendung': '',
    'konto': '',
    'value': '',
    'debitor_id': '',
    'mandats_ref': '',
    'customer_ref': '',
    'src_konto': '',
}

def validate_konto(value):
    if 'DE' not in value:
        raise ValidationError('%(value)s is not an account', params={'value': value})


class Transactions(models.Model):
    tdate = models.DateField(blank=False)
    status = models.CharField(max_length=20)
    debitor = models.CharField(max_length=100)
    verwendung = models.CharField(max_length=300)
    konto = models.CharField(max_length=100,
                             validators=[validate_konto])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    debitor_id = models.CharField(max_length=100)
    mandats_ref = models.CharField(max_length=100)
    customer_ref = models.CharField(max_length=100)
    src_konto =models.CharField(max_length=100)
    text = models.CharField(max_length=300)
    hash = models.CharField(max_length=300) 

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hash'], name='unique_transaction_hash')
        ]
        verbose_name = 'Transaction'


class History(models.Model):
    import_date = models.DateTimeField(auto_now=True)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=10)
    account = models.CharField(max_length=100)
    max_date = models.DateField(blank=False)
    min_date = models.DateField(blank=False)
    hash = models.CharField(max_length=300)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hash'], name='unique_history_hash')
        ]


class EUR(models.Model):
    CYCLE_CHOICES = [('daily', 'daily'),
                     ('weekly', 'weekly'),
                     ('monthly', 'monthly'),
                     ('yearly', 'yearly')]
    position = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, default='TBD')
    inout = models.CharField(max_length=5)
    priority = models.CharField(max_length=50, default='TBD')
    cycle = models.CharField(max_length=50,
                            choices=CYCLE_CHOICES,
                            default=CYCLE_CHOICES[2],) 
    ROI = models.TextField(blank=True)
    note = models.TextField(blank=True)
    daily = models.DecimalField(max_digits=10, decimal_places=2)
    weekly = models.DecimalField(max_digits=10, decimal_places=2)
    monthly = models.DecimalField(max_digits=10, decimal_places=2)
    yearly = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(default="", null=False, db_index=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.position)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.position} ({self.value})"
    

class Mapping(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.PROTECT, related_name='transaction')
    eur = models.ForeignKey(EUR, on_delete=models.PROTECT, related_name='eur')