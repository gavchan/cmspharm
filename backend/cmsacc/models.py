from django.db import models

class Bill(models.Model):
    """
    Maps to CMS table to track bills charged to patient:encounter_id
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    encounter_id = models.BigIntegerField(blank=True, null=True)
    invoice_print_status = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    receipt_print_status = models.BooleanField(default=False)
    total = models.FloatField()
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    transaction_code = models.CharField(max_length=255, blank=True, null=True)
    unbalance_amt = models.FloatField(default=0)
    daily_sequence_per_clinic = models.IntegerField(blank=True, null=True)
    payment_update_count = models.IntegerField(blank=True, null=True)
    temp_wq_arrive_time = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bill'
        app_label = 'cmsacc'
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.date_created} | Encounter #{self.encounter_id} Total ${self.total}; Unbalanced ${self.unbalance_amt}"


class BillDetail(models.Model):
    """
    Maps to CMS table to track billing details
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    bill = models.ForeignKey(
        'Bill', on_delete=models.PROTECT,
        db_column='bill_id'
        )
    # billed_amount = standard x discount_percent
    billed_amount = models.FloatField()
    charge_item = models.ForeignKey(
        'ChargeItem', on_delete=models.PROTECT,
        db_column='charge_item_id'
    )
    remarks = models.TextField(blank=True, null=True)

    # standard - standard cost of charge item
    standard = models.FloatField()

    # bill_details_idx - index number of item linked to the same bill_id
    bill_details_idx = models.IntegerField(blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    quantity = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bill_detail'
        app_label = 'cmsacc'
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.last_updated} | #{self.bill.id}.{self.bill_details_idx}: {self.charge_item.alias} - ${self.billed_amount} (Std ${self.standard})"

class Cashbook(models.Model):
    """
    CMS table to track cash transactions
    """
    BILL = 'bill'  # all lowercase used in CMS app
    DELIVERY = 'Delivery'
    DISPENSARY = 'Dispensary'
    REMARK_CHOICES = [
        (DELIVERY, 'Delivery'),
        (DISPENSARY, 'Dispensary'),
    ]
    ENTRY_TYPE_CHOICES = [
        (BILL, 'Bill'),
        (DELIVERY, 'Delivery'),
    ]
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    amount = models.FloatField()
    date_created = models.DateField(auto_now_add=True)
    editable = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # reference_id - refers to if in CMS table specified in entry_type
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    remark = models.TextField(choices=REMARK_CHOICES, blank=True, null=True)
    entry_type = models.CharField(
        choices=ENTRY_TYPE_CHOICES,
        max_length=255, blank=True, null=True,
        db_column='type'
        )
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cashbook'
        app_label = 'cmsacc'
        verbose_name_plural = 'Cashbook'
        ordering = ['-id']

    def __str__(self):
        return f"{self.id} | {self.date_created} {self.entry_type} #{self.reference_id} - ${self.amount}"

class ChargeItem(models.Model):
    """
    CMS table to track service item charge
    """
    id = models.BigAutoField(primary_key=True)
    version = models.BigIntegerField(default=0)
    alias = models.CharField(max_length=255)
    # cp_prescription_amt - '1' for medication, '0' for all other items
    cp_prescription_amt = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    description_chinese = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    owner_id = models.BigIntegerField(blank=True, null=True)
    standard_amount = models.FloatField()
    cp_consumable_amt = models.BooleanField(default=False)
    inactive = models.BooleanField(default=False)
    sys_is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'charge_item'
        app_label = 'cmsacc'
        ordering = ['alias']

    def __str__(self):
        return f"{self.alias} | ${self.standard_amount} - {self.description_chinese} {self.description}"
