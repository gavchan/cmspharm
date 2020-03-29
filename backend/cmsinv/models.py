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


class InventoryItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField()

    advisory = models.ForeignKey('Advisory', on_delete=models.PROTECT)
    
    alias = models.CharField(max_length=255, blank=True, null=True)
    avg_cost = models.FloatField(default=0)
    category = models.CharField(max_length=255, blank=True, null=True)
    certificate_holder_id = models.BigIntegerField(blank=True, null=True)
    clinic_drug_no = models.CharField(max_length=255, blank=True, null=True)
    dangerous_sign = models.BooleanField(default=False)
    date_created = models.DateTimeField(blank=True, null=True)
    discontinue = models.BooleanField(default=False)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=255, blank=True, null=True)
    expected_qty = models.FloatField()
    expire_date = models.DateField(blank=True, null=True)
    frequency = models.CharField(max_length=255, blank=True, null=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    generic_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    ingredient = models.TextField(blank=True, null=True)
    
    instruction = models.ForeignKey('Instruction', on_delete=models.PROTECT)
    
    inventory_type = models.CharField(max_length=255, blank=True, null=True)
    is_clinic_drug_list = models.BooleanField(default=True)
    is_master_drug_list = models.BooleanField(default=True)
    label_name = models.CharField(max_length=255, blank=True, null=True)
    label_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    mini_dispensary_unit = models.FloatField()
    mini_dosage_unit = models.FloatField()
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_name_chinese = models.CharField(max_length=255, blank=True, null=True)
    registration_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    reorder_level = models.FloatField()
    reorder_status = models.CharField(max_length=255, blank=True, null=True)
    standard_cost = models.FloatField(default=0)
    stock_qty = models.FloatField()
    unit = models.CharField(max_length=255, blank=True, null=True)
    unit_price = models.FloatField(default=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    priority = models.FloatField(blank=True, null=True)

    inventory_item_type = models.ForeignKey('InventoryItemType', on_delete=models.PROTECT, db_column='type_id')

    class Meta:
        managed = False
        db_table = 'inventory_item'
        app_label = 'cmsinv'

    def __str__(self):
        return '{} | {} / {} [{}]'.format(
            self.registration_no, self.product_name, self.generic_name, self.alias
        )