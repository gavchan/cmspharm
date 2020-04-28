from django.db import models
from django.urls import reverse

class ItemType(models.Model):
    """
    Model for type of inventory items, correlates to cmsinv.InventoryItemType
    To reserve id=1 for Drug, id=2 for Consumable
    """
    version = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']
        verbose_name = 'Item type'

    def __str__(self):
        return f"{self.id} | {self.name}"

class Category(models.Model):
    """
    Model for non-drug inventory items category
    """
    version = models.BigIntegerField(default=0)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name}"

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
    version = models.BigIntegerField(default=0)
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
    account_no = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('inventory:VendorUpdate', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name}"

class Item(models.Model):
    """
    Model for non-drug inventory items
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    version = models.BigIntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        blank=True, null=True,
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT,
    )
    active = models.BooleanField(default=True)
    discontinue = models.BooleanField(default=False)
    inventory_type = models.ForeignKey(
        ItemType, on_delete=models.PROTECT,
        default=2, # 2=Consumable
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('inventory:ItemDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name} [{self.vendor.name}]"

class Delivery(models.Model):
    """
    Abstract base class that is inherited by `DrugDelivery` and `ItemDelivery`
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
    received_date = models.DateField(auto_now_add=True)
    received_by = models.CharField(max_length=255, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
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
        return round(self.unit_price * self.purchase_quantity / self.items_quantity, 2) 

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


class ItemDelivery(Delivery):
    """
    Records consumable purchase transactions
    """ 
    
    items_unit = models.ForeignKey(
        ItemsUnit, on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['received_date']
        verbose_name = 'Item delivery'
        verbose_name_plural = 'Item deliveries'

    def get_absolute_url(self):
        return reverse('inventory:ItemDeliveryDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.date_created} | {self.product_name} [{self.purchase_quantity}+{self.bonus_quantity}] ${self.total_price}"