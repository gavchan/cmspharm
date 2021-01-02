from django.db import models
from django.urls import reverse
from cmsinv.models import InventoryItem
from inventory.models import Delivery
from ledger.models import Expense
import re

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs registered in offical drug office database
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    # name: Product Name
    reg_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    itemid = models.PositiveIntegerField(blank=True, null=True, unique=True)
    # reg_no: equivalent to "permit_no" in drug database
    ingredients_str = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    ingredients = models.ManyToManyField(
        'Ingredient', 
        related_name='registereddrugs',
    )
    company = models.ForeignKey(
        'Company', on_delete=models.PROTECT,
        )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['reg_no']
        verbose_name = 'Registered drug'
  
    @property
    def ingredients_list(self):
        return ", ".join([i.name for i in self.ingredients.all()])

    @property
    def gen_dosage(self):
        """
        Tries to get dosage from product name
        Patterns:
        - Oral meds:    [Number] [MG]
                        [Number] [MCG]
        - Syrup meds:   [Number][MG]/[Number][ML]
        - Injections:   [Number][MCG/ML]
        - Inhaled:      [Number][MCG/SPRAY]
        - External:     [Number]%
        """
        pattern = re.compile(r'(\d*\.?\d*\s?(MC?G)\/?(\d*\.?\d*)?(MG|MCG|ML|SPRAY)?)|(\d*\.?\d*\%)/g', re.IGNORECASE)
        dose_search = pattern.search(self.name)

        if dose_search:
            return dose_search.group()
        else:
            return ""

    @property
    def gen_generic(self):
        """
        Generate generic name from ingredients
        For drugs with <= 3 ingredients, use first word of ingredient
        For drugs with >3 ingredients, return "COMBO"
        """

        first_words = []
        if len(self.ingredients.all()) <=5:
            for ingr in self.ingredients.all():
                first_words.append(ingr.name.split()[0])
            return " / ".join(first_words)
        else:
            for ingr in self.ingredients.all():
                first_words.append(ingr.name.split()[0])
            return "COMBO: " + " / ".join(first_words[:5]) + "..."

    
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
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.name}"

class Ingredient(models.Model):
    """
    Stores list of ingredients
    """
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# class DrugDelivery(Delivery):
#     """
#     Records drug purchase transactions
#     """
#     AMPOULE = 'AMPOULE'
#     BOTTLE = 'BOTTLE'
#     BOX = 'BOX'
#     CAPSULE = 'CAP'
#     DOSE = 'DOSE'
#     GRAM = 'GRAM'
#     INJECTION = 'INJECTION'
#     MG = 'MG'
#     ML = 'ML'
#     PACK = 'PACK'
#     TAB = 'TAB'
#     TUBE = 'TUBE'
#     UNIT = 'UNIT'
#     VIAL = 'VIAL'

#     ITEMS_UNIT_CHOICES = [
#         (AMPOULE, 'Ampoule'),
#         (BOTTLE, 'Bottle'),
#         (BOX, 'Box'),
#         (CAPSULE, 'Cap'),
#         (DOSE, 'Dose'),
#         (GRAM, 'gram'),
#         (INJECTION, 'Injection'),
#         (MG, 'mg'),
#         (ML, 'mL'),
#         (PACK, 'Pack'),
#         (TAB, 'Tablet'),
#         (TUBE, 'Tube'),
#         (UNIT, 'Unit'),
#         (VIAL, 'Vial'),
#     ]
#     reg_no = models.CharField(max_length=255, blank=True, null=True)
#     cmsinv_item = models.ForeignKey(
#         InventoryItem, on_delete=models.CASCADE,
#         blank=True, null=True,
#         )
#     bill = models.ForeignKey(
#         Expense, on_delete=models.CASCADE,
#         blank=True, null=True,
#     )
#     items_unit = models.CharField(max_length=100, choices=ITEMS_UNIT_CHOICES, default=TAB)

#     class Meta:
#         verbose_name = 'Drug delivery'
#         verbose_name_plural = 'Drug deliveries'

#     def get_absolute_url(self):
#         return reverse('drugdb:DrugDeliveryDetail', kwargs={'pk': self.pk})