from django.db import models
from inventory.models import Delivery

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    # name: Product Name
    registration_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # registration_no: equivalent to "permit_no" in drug database
    ingredients = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    company = models.ForeignKey(
        'Company', on_delete=models.PROTECT,
        )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['registration_no']
  
    def __str__(self):
        return f"{self.registration_no} | {self.name}"

class Company(models.Model):
    """
    Stores list of company names and addresses
    """
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_certholder = models.BooleanField(default=True)
    # is_certholder: Companies imported from drug database are certificate holders 
    is_supplier = models.BooleanField(default=False)
    # is_supplier: Companies may also be a supplier
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

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
        (AMPOULE, 'AMPOULE'),
        (BOTTLE, 'BOTTLE'),
        (BOX, 'BOX'),
        (CAPSULE, 'CAP'),
        (DOSE, 'DOSE'),
        (GRAM, 'GRAM'),
        (INJECTION, 'INJECTION'),
        (MG, 'MG'),
        (ML, 'ML'),
        (PACK, 'PACK'),
        (TAB, 'TAB'),
        (TUBE, 'TUBE'),
        (UNIT, 'UNIT'),
        (VIAL, 'VIAL'),
    ]
    registration_no = models.CharField(max_length=255, blank=True, null=True)
    items_unit = models.CharField(max_length=100, choices=ITEMS_UNIT_CHOICES, default=TAB)