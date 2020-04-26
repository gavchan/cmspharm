from django.db import models
from django.urls import reverse
from inventory.models import Delivery

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs registered in offical drug office database
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    # name: Product Name
    reg_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # reg_no: equivalent to "permit_no" in drug database
    ingredients = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    company = models.ForeignKey(
        'Company', on_delete=models.PROTECT,
        )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['reg_no']
  
    def __str__(self):
        return f"{self.reg_no} | {self.name}"

class Company(models.Model):
    """
    Stores list of company names and addresses in official drug office database
    """
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_certholder = models.BooleanField(default=True)
    # is_certholder: Companies imported from drug database are certificate holders 
    is_supplier = models.BooleanField(default=False)
    # is_supplier: Companies may also be a supplier
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.name}"

class DrugDelivery(Delivery):
    """
    Records drug purchase transactions
    """
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
    reg_no = models.CharField(max_length=255, blank=True, null=True)
    items_unit = models.CharField(max_length=100, choices=ITEMS_UNIT_CHOICES, default=TAB)

    def get_absolute_url(self):
        return reverse('drugdb:DrugDeliveryDetail', kwargs={'pk': self.pk})