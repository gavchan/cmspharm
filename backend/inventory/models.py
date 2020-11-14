from django.db import models
from django.urls import reverse
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
    value = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Item type'

    def __str__(self):
        return f"{self.value} | {self.name}"

class Item(models.Model):
    """
    Model for non-drug inventory items
    """
    # ITEM_UNIT Choices
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

    ITEM_UNIT_CHOICES = [
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
    name = models.CharField(max_length=255, blank=True, null=True)
    cms = models.ForeignKey(
        InventoryItem, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    item_type = models.ForeignKey(
        ItemType, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    item_unit = models.CharField(max_length=100, choices=ITEM_UNIT_CHOICES, default=TAB)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('inventory:ItemDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name}"

class Delivery(models.Model):  ### To be superceded by DeliveryOrder ###
    """
    Abstract base class that is inherited by `DrugDelivery`
    """

    PACK = 'PACK'
    BOX = 'BOX'

    PURCHASE_UNIT_CHOICES = [
        (PACK, 'Pack'),
        (BOX, 'Box'),
    ]
 
    product_name = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    delivery_note_no = models.CharField(max_length=255, blank=True, null=True)
    # delivery_note_no: can be referenced to cmsinv.Delivery; a.k.a. invoice no.
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    purchase_unit = models.CharField(max_length=100, choices=PURCHASE_UNIT_CHOICES, default=PACK)
    bonus_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    # discount: percentage discount applied to unit_price in calculation of total; e.g. 25 = 25% off
    items_per_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    # items_per_purchase: number of granular items per unit of purchase. E.g. 1 pack can contain 100 items
    # items_unit: defined in respective model (ConsumableDelivery, DrugDelivery)
    batch_num = models.CharField(max_length=100, blank=True, null=True)
    other_ref = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    received_date = models.DateField()
    received_by = models.CharField(max_length=255, blank=True, null=True)
    expiry_month = models.CharField(max_length=8, default="", blank=True, null=True)
    # expiry_month: format of yyyymm, or yyyymmdd; to supercede expiry_date
    expiry_date = models.DateField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

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
            std_cost = round(self.unit_price * self.purchase_quantity / (self.items_per_purchase * self.purchase_quantity), 2)
        except Exception as e:
            print('%s (%s)' % (e, type(e))) 
            std_cost = 'NA'
        return  std_cost

    @property
    def average_cost(self):
        """Average cost of items (including bonus items and discounts)"""
        return round(self.total_price / self.items_quantity, 2)
    
    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Deliveries'
    
    # def get_absolute_url(self):
    #     return reverse('DeliveryDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.date_created} | {self.product_name} [{self.purchase_quantity}+{self.bonus_quantity}] ${self.total_price}"

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
    payee = models.CharField(max_length=255, blank=True, null=True)
    # vendor: can be the same as the payee; occasionally the payee name is different.
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    bill = models.ForeignKey(
        'ledger.Expense', on_delete=models.PROTECT,
        blank=True, null=True,
    )
    payment_method = models.ForeignKey(
        'ledger.PaymentMethod', on_delete=models.PROTECT,
    )
    # payment_ref: used for cheque number or other
    payment_ref = models.CharField(verbose_name="Cheque/ref no.", max_length=255, blank=True, null=True)
    expected_date = models.DateField(verbose_name="Cheque/paid date", blank=True, null=True)
    other_ref = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-invoice_date']

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
    item = models.ForeignKey(
        Item, related_name='delivery_items',
        on_delete=models.CASCADE,
    )
    delivery_order = models.ForeignKey(
        DeliveryOrder, related_name='delivery_items',
        on_delete = models.CASCADE,
    )
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    purchase_unit = models.CharField(max_length=100, choices=PURCHASE_UNIT_CHOICES, default=PACK)
    bonus_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=0, default=0)
    # discount: percentage discount applied to unit_price in calculation of total; e.g. 25 = 25% off
    items_per_purchase = models.DecimalField(max_digits=10, decimal_places=0, default=1)
    # items_per_purchase: number of granular items per unit of purchase. E.g. 1 pack can contain 100 items
    # items_unit: defined in respective model (ConsumableDelivery, DrugDelivery)
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
            std_cost = round(self.unit_price * self.purchase_quantity / (self.items_per_purchase * self.purchase_quantity), 2)
        except Exception as e:
            print('%s (%s)' % (e, type(e))) 
            std_cost = 'NA'
        return  std_cost

    @property
    def average_cost(self):
        """Average cost of items (including bonus items and discounts)"""
        return round(self.total_price / self.items_quantity, 2)
