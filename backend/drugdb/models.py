from django.db import models
from cmsinv.models import InventoryItem, Supplier, Depletion, DepletionItem

class RegisteredDrug(models.Model):
    """
    Stores list of products/drugs
    """
    # Product Name
    name = models.CharField(max_length=255, blank=True, null=True)
    # Permit No.
    permit_no = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # Active ingredients
    ingredients = models.TextField(blank=True, null=True)
    # Company Name and Company Address
    company = models.ForeignKey(
        'Company', on_delete=models.CASCADE,
        )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['permit_no']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('drugdb.views.details', args=[str(self.permit_no)])
  
    def __str__(self):
        return '{} | {} ({})'.format(
            self.permit_no, self.name, self.ingredients
        )

class Company(models.Model):
    """
    Stores list of company names and addresses
    """
    # Company Name
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    # Company Address
    address = models.TextField(blank=True, null=True)
    # Companies imported from official source are certificate holders
    is_certholder = models.BooleanField(default=True)
    # Companies may also be a supplier
    is_supplier = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('drugdb.views.details', args=[str(self.id)])
    
    def __str__(self):
        return '{}'.format(
            self.name
        )

# class InventoryItemSupplier(models.Model):
#     """
#     Maps to CMS table: inventory_item_supplier_manufacturer
#     Stores which inventory_items are supplied by which supplier_manufacturer

#     CMS table inventory_item_supplier_manufacturer is a legacy table using a composite key as the primary key
#     Django does not support composite keys and a many-to-many field could not be used for this table
#     Await solution/implementation/workaround...
#     Without a solution in the legacy, table, attempt to build a surrogate table in default db
#     """
#     id = models.BigAutoField(primary_key=True)
#     inventory_item = models.ForeignKey(
#         'cmsinv.InventoryItem', on_delete=models.PROTECT,
#         db_column='inventory_item_suppliers_id'
#         )
#     supplier = models.ForeignKey(
#         'cmsinv.Supplier', on_delete=models.PROTECT,
#         db_column='supplier_manufacturer_id'
#         )
#     suppliers_idx = models.IntegerField(default=0, blank=True, null=True)

#     class Meta:
#         unique_together = ['inventory_item', 'supplier']
#         # db_table = 'inventory_item_supplier_manufacturer'
#         ordering = ['id']
#         app_label = 'drugdb'

#     def __str__(self):
#         return f"{self.supplier.name} - {self.suppliers_idx} : {self.inventory_item.product_name}"

# class DepletionDepletionItem(models.Model):
#     """
#     CMS table depletion_depletion_items is a legacy table using a composite key as the primary key
#     Django does not support composite keys and a many-to-many field could not be used for this table
#     Will have errors when trying to write/save/view details
#     Await solution/implementation/workaround...
#     Without a solution in the legacy, table, attempt to build a surrogate table in default db
#     """
#     id = models.BigAutoField(primary_key=True)
#     depletion = models.ForeignKey(
#         'cmsinv.Depletion', on_delete=models.PROTECT,
#         db_column='depletion_items_id'
#         )
#     depletion_item = models.ForeignKey(
#         'cmsinv.DepletionItem', on_delete=models.PROTECT,
#         db_column='depletion_item_id'
#     )
#     items_idx = models.IntegerField(blank=True, null=True)

#     class Meta:
#         unique_together = ['depletion', 'depletion_item']
#         # db_table = 'depletion_depletion_item'
#         ordering = ['id']
#         app_label = 'drugdb'

#     def __str__(self):
#         return '{} [{}] {}'.format(
#             self.depletion, self.items_idx, self.depletion_item
#         )

