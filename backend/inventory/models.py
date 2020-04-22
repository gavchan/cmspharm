from django.db import models
from django.urls import reverse

# Create your models here.
class Delivery(models.Model):
    """
    Abstract base class that is inherited by `DrugPurchase` and `ConsumablePurchase`
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
    purchase_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_unit = models.CharField(max_length=100, choices=PURCHASE_UNIT_CHOICES, default=PACK)
    bonus_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    # discount: percentage discount applied to unit_price in calculation of total; e.g. 25 = 25% off
    items_per_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    # items_per_purchase: number of granular items per unit of purchase. E.g. 1 pack can contain 100 items
    # items_unit: defined in respective model (ConsumableDelivery, DrugDelivery)
    batch_num = models.CharField(max_length=100, blank=True, null=True)
    other_ref = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(auto_now_add=True)
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
    
    def get_absolute_url(self):
        return reverse('DeliveryDetail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.date_created} | {self.product_name} [{self.purchase_quantity}+{self.bonus_quantity}] ${self.total_price}"

class ConsumableDelivery(Delivery):
    """
    Records consumable purchase transactions
    """
    MEDICAL = 'MED'
    MISC = 'MISC'
    
    CATEGORY_CHOICES = [
        (MEDICAL, 'Medical'),
        (MISC, 'Miscellaneous'),
    ]
    
    PIECE = 'PC'
    
    ITEMS_UNIT_CHOICES = [
        (PIECE, 'Piece'),
    ]
    
    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, default=MEDICAL)
    items_unit = models.CharField(max_length=100, choices=ITEMS_UNIT_CHOICES, default=PIECE)