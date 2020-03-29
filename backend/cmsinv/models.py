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
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | {} - {}'.format(
            self.id, self.name, self.supp_type
        )

class Advisory(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    alias = models.CharField(unique=True, max_length=255)
    created_by_cmsuser_id = models.BigIntegerField(db_column='created_by_id', blank=True, null=True)
    date_created = models.DateTimeField()
    description = models.TextField()
    description_chinese = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    last_updated = models.DateTimeField()
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advisory'
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | {} / {}'.format(
            self.alias, self.description_chinese, self.description
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
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | {} / {}'.format(
            self.alias, self.description_chinese, self.description
        )

class InventoryItemType(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'inventory_item_type'
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | {}'.format(
            self.id, self.name
        )
