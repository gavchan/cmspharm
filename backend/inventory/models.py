from datetime import datetime
import pytz
from django.db import models
from django.urls import reverse
from django.conf import settings
# from drugdb.models import RegisteredDrug
# from ledger.models import ExpenseCategory
from cmsinv.models import InventoryItem

class Category(models.Model):
    """
    Model for item category
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    value = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['value']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.value} | {self.name}"

    def get_absolute_url(self):
        return reverse('inventory:CategoryUpdate', kwargs={'pk': self.pk})

class Vendor(models.Model):
    """
    Model for vendor/suppliers
    """
    # Fields matching drugdb.Company
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Fields matching cmsinv.Supplier
    # Note: tel_home replaced by tel_main
    #       version converted from BigIntegerField to PositiveIntegerField
    version = models.PositiveIntegerField(default=1)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    tel_main = models.CharField(max_length=255, blank=True, null=True)
    tel_mobile = models.CharField(max_length=255, blank=True, null=True)
    tel_office = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    
    # Below commented field from cmsinv.Supplier omitted
    # supp_type = models.CharField(db_column='type', choices=SUPP_TYPE_CHOICES, max_length=255, blank=True, null=True)

    # Extra fields
    alias = models.CharField(unique=True, max_length=255, blank=True, null=True)
    account_no = models.CharField(max_length=255, blank=True, null=True)
    is_supplier = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    default_exp_category = models.ForeignKey(
        'ledger.ExpenseCategory', on_delete=models.PROTECT,
        verbose_name="Default expense category",
        blank=True, null=True
    )
    default_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['name']
        permissions = (
            ('can_view_supplier', 'Can view supplier'),
            ('can_change_supplier', 'Can change supplier'),
        )
    def get_absolute_url(self):
        return reverse('inventory:VendorUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name}"

class ItemType(models.Model):
    """
    Model for type of inventory items, correlates to cmsinv.InventoryItemType
    To reserve id=1 for Drug, id=2 for Consumable
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    value = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Item type'

    def __str__(self):
        return f"{self.value} | {self.name}"

class Item(models.Model):
    """
    Model to link CMS inventory item from external database, registered drug
    """
    
    name = models.CharField(max_length=255)  
    # name: Not enforce unique as Govt Drug Database and CMS product_name can have duplicate names
    note = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    cmsid = models.PositiveIntegerField(blank=True, null=True)
    reg_no = models.CharField(max_length=255, blank=True, null=True)
    item_type = models.ForeignKey(
        ItemType, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('inventory:ItemDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name}"

class ItemsUnit(models.Model):
    """
    Records item units, e.g. pieces, bottles, mls etc.
    """
    short = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['short']

    def __str__(self):
        return f"{self.short}: {self.name}"


class DeliveryOrder(models.Model):
    """
    Records delivery orders
    """
    invoice_no = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    items = models.ManyToManyField(
        Item, through='DeliveryItem',
        related_name='delivery_orders',
        blank=True)
    received_date = models.DateField(blank=True, null=True)
    received_by = models.CharField(max_length=255, blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor, blank=True, null=True,
        on_delete = models.PROTECT
        )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    bill = models.ForeignKey(
        'ledger.Expense', on_delete=models.PROTECT,
        blank=True, null=True,
    )
    due_date = models.DateField(blank=True, null=True)
    other_ref = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    cms_synced = models.BooleanField(default=False)
    cms_delivery_id = models.BigIntegerField(blank=True, null=True, default=None)
    version = models.PositiveIntegerField(default=1)

    @property
    def item_summary(self):
        return ', '.join(item.name for item in self.items.all())

    @property
    def items_total(self):
        total = 0
        for listitem in self.delivery_items.all():
            total += listitem.total_price
        return total

    class Meta:
        ordering = ['-invoice_date']

    def __str__(self):
        return f"{self.received_date} : ${self.amount} | {self.vendor.name}"

    def get_absolute_url(self):
        return reverse('inventory:DeliveryOrderDetail', kwargs={'pk': self.pk})


class DeliveryItem(models.Model):
    """
    Records item purchase transactions per DeliveryOrder
    """
    PACK = 'PACK'
    BOX = 'BOX'

    PURCHASE_UNIT_CHOICES = [
        (PACK, 'Pack'),
        (BOX, 'Box'),
    ]

    AMPOULE = 'AMPOULE'
    BOTTLE = 'BOTTLE'
    BOX = 'BOX'
    CAPSULE = 'CAP'
    DOSE = 'DOSE'
    GRAM = 'GRAM'
    INJECTION = 'INJECTION'
    MG = 'MG'
    ML = 'ML'
    PACK = 'PACK'
    TAB = 'TAB'
    TUBE = 'TUBE'
    UNIT = 'UNIT'
    VIAL = 'VIAL'

    ITEMS_UNIT_CHOICES = [
        (AMPOULE, 'Ampoule'),
        (BOTTLE, 'Bottle'),
        (BOX, 'Box'),
        (CAPSULE, 'Cap'),
        (DOSE, 'Dose'),
        (GRAM, 'gram'),
        (INJECTION, 'Injection'),
        (MG, 'mg'),
        (ML, 'mL'),
        (PACK, 'Pack'),
        (TAB, 'Tablet'),
        (TUBE, 'Tube'),
        (UNIT, 'Unit'),
        (VIAL, 'Vial'),
    ]

    item = models.ForeignKey(
        Item, related_name='delivery_items',
        on_delete=models.CASCADE,
    )
    delivery_order = models.ForeignKey(
        DeliveryOrder, related_name='delivery_items',
        on_delete = models.CASCADE,
    )
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    purchase_unit = models.CharField(max_length=100, choices=PURCHASE_UNIT_CHOICES, default=BOX)
    bonus_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=0, default=0)
    # discount: percentage discount applied to unit_price in calculation of total; e.g. 25 = 25% off
    items_per_purchase = models.DecimalField(max_digits=10, decimal_places=0, default=1)
    # items_per_purchase: number of granular items per unit of purchase. E.g. 1 pack can contain 100 items
    items_unit = models.CharField(max_length=10, choices=ITEMS_UNIT_CHOICES, blank=True, null=True)
    batch_num = models.CharField(max_length=100, blank=True, null=True)
    other_ref = models.CharField(max_length=100, blank=True, null=True)
    expiry_month = models.CharField(verbose_name='Expiry (YYYYMM)',max_length=8, default="", blank=True, null=True)
    is_sample = models.BooleanField(default=False)
    # expiry_month: format of yyyymm, or yyyymmdd; to supercede expiry_date
    version = models.PositiveIntegerField(default=1)

    # Calculated properties
    @property
    def total_price(self):
        """Total calculated price of purchased unit in transaction"""
        return round(self.purchase_quantity * self.unit_price * (1 - self.discount/100), 2)

    @property
    def items_quantity(self):
        """Total calculated number of items including bonus in transaction"""
        return round(self.items_per_purchase * (self.purchase_quantity + self.bonus_quantity), 2)

    @property
    def standard_cost(self):
        """Standard average cost of items (not including bonus items or discounts)"""
        try:
            if self.is_sample:
                std_cost = round(self.unit_price * self.bonus_quantity / (self.items_per_purchase * self.bonus_quantity), 2)
            else:
                std_cost = round(self.unit_price * self.purchase_quantity / (self.items_per_purchase * self.purchase_quantity), 2)
        except ZeroDivisionError:
            std_cost = 0.0
        return  std_cost

    @property
    def average_cost(self):
        """Average cost of items (including bonus items and discounts)"""
        try:
            avg_cost = round(self.total_price / self.items_quantity, 2)
        except ZeroDivisionError:
            avg_cost = 0.00
        return avg_cost

    @property
    def expiry_str(self):
        if self.expiry_month:
            if len(self.expiry_month) == 6:
                return(self.expiry_month[:4] + '-' + self.expiry_month[4:])
            elif len(self.expiry_month) == 8:
                return(self.expiry_month[:4] + '-' + self.expiry_month[4:6] + '-' + self.expiry_month[6:])
            else:
                return(self.expiry_month)
        else:
            return None
    
    @property
    def expiry_date(self):
        if self.expiry_month:
            if len(self.expiry_month) == 6:
                btime = datetime.strptime(self.expiry_month, "%Y%m")
                return btime.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            elif len(self.expiry_month) == 8:
                btime = datetime.strptime(self.expiry_month, "%Y%m%d")
                return btime.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            else:
                return None
        else:
            return None

    @property
    def terms(self):
        purchase_str = str(self.purchase_quantity)
        purchase_str = purchase_str.rstrip('0').rstrip('.') if '.' in purchase_str else purchase_str
        bonus_str = str(self.bonus_quantity)
        bonus_str = bonus_str.rstrip('0').rstrip('.') if '.' in bonus_str else bonus_str
        if self.purchase_quantity == 0:
            if self.bonus_quantity != 0:
                # Sample
                terms = "Sample; "
            else:
                # No purchase/bonus quantity
                terms = "Zero; "
        else:
            if self.bonus_quantity == 0:
                # No special terms
                terms = purchase_str + self.purchase_unit
            else:
                # Bonus terms
                terms = purchase_str + "+" + bonus_str + " " + self.purchase_unit
        if self.items_unit:
            items_unit = self.items_unit
        else:
            items_unit = "units"
        terms = f"{terms} x{self.items_per_purchase}{items_unit}"
        return terms
