from django.db import models
from django.urls import reverse
# Create your models here.


class Property(models.Model):
    name = models.CharField(max_length=256)
    inout = models.CharField(max_length=250)
    type = models.CharField(max_length=250)
    cycle = models.CharField(max_length=250)

    def __str__(self) -> str:
        return str(self.name)


class History(models.Model):
    """Datclass of History, for importing into DB
    """
    file_name = models.CharField(max_length=250)
    file_type = models.CharField(max_length=250)
    account = models.CharField(max_length=250)
    import_date = models.DateField()
    max_date = models.DateField()
    min_date = models.DateField()
    checksum = models.CharField(max_length=250)

    def __str__(self) -> str:
        return str(self.file_name)


class Transaction(models.Model):
    date = models.DateField()
    text = models.CharField(max_length=500)
    status = models.CharField(max_length=250)
    debitor = models.CharField(max_length=250, null=True, blank=True)
    verwendung = models.CharField(max_length=250)
    konto = models.CharField(max_length=250)
    debitor_id = models.CharField(max_length=250, null=True, blank=True)
    mandats_ref = models.CharField(max_length=250, null=True, blank=True)
    customer_ref = models.CharField(max_length=250, null=True, blank=True)
    src_konto = models.CharField(max_length=250)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    properties = models.ForeignKey(Property,
                                 related_name='properties',    # this is the name which will be used in the template
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True
                                 )


    def get_absolute_url(self):
        return reverse("home:trans_detail", kwargs={'pk':self.pk})

    def save(self, **kwargs):
        # do_something()
        super().save(**kwargs)  # Call the "real" save() method.
        # do_something_else()

    def __str__(self):
        return f'{self.date} - {self.value} - {self.text}'
