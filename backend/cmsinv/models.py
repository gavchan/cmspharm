from django.db import models

class SupplierManufacturer(models.Model):
    """Links to CMS table for supplier/cert holder/manufacturer"""
    CERT_HOLDER = 'Certificate Holder'
    SUPPLIER = 'Supplier'
    MANUFACTURER = 'Manufacturer'
    SUPP_TYPE_CHOICES = [
        (CERT_HOLDER, 'Certificate Holder'),
        (SUPPLIER, 'Supplier'),
        (MANUFACTURER, 'Manufacturer'),
    ]
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField()
    email = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField()
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    tel_home = models.CharField(max_length=255, blank=True, null=True)
    tel_mobile = models.CharField(max_length=255, blank=True, null=True)
    tel_office = models.CharField(max_length=255, blank=True, null=True)
    supp_type = models.CharField(db_column='type', choices=SUPP_TYPE_CHOICES, max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplier_manufacturer'

    def __str__(self):
        return '{} | {} - {}'.format(
            self.id, self.name, self.supp_type
        )

class Instruction(models.Model):
    """CMS table for medication use instruction templates"""
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    alias = models.CharField(unique=True, max_length=255)
    created_by_cmsuser_id = models.BigIntegerField(db_column='created_by_id', blank=True, null=True)
    date_created = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    description_chinese = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    last_updated = models.DateTimeField()
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instruction'

    def __str__(self):
        return '{} | {} / {}'.format(
            self.alias, self.description_chinese, self.description
        )
