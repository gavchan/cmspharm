import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug, Company, Ingredient
from cmsinv.models import (
    InventoryItem, Prescription, PrescriptionDetail, InventoryMovementLog,
    DepletionItem, ReceivedItem, Supplier, InventoryItemType
)
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Cleans CMS SuppliersManufacturers database table
    - Remove unused
    - Match reg_no - if exist, match company
    """
    help = 'Cleans CMS InventoryItem database - mark unused items for Trash'

        
    def handle(self, *args, **kwargs):
        print("Reset all InventoryItems with valid reg_no - SupplierManufacturer to !__NA__!")
        supplier_na = Supplier.objects.get(name='!__NA__!')
        processed = 0
        for cmsitem in InventoryItem.objects.all():
            cmsitem.certificate_holder = supplier_na
            cmsitem.save()
            processed += 1
            sys.stdout.write('.')

        print(f"\nProcessed InventoryItems: {processed}")
        print("Deleting all existing SupplierManufacturers")
        suppliers_to_delete = Supplier.objects.exclude(name='!__NA__!')
        deleted = 0
        for supplier in suppliers_to_delete:
            supplier.delete()
            deleted += 1
            sys.stdout.write('.')
        print(f"\nDeleted SupplierManufacturers: {deleted}")

        print(f"\nRebuild SupplierManufacturer database table and set InventoryItems")
        processed = 0
        linked = 0
        new_suppliers = 0
        drugtype = InventoryItemType.objects.get(id=1)
        for cmsitem in InventoryItem.objects.all():
            processed += 1
            try:
                drug_obj = RegisteredDrug.objects.get(reg_no=cmsitem.registration_no)
            except RegisteredDrug.DoesNotExist:
                drug_obj = None
                sys.stdout.write('o')
            if drug_obj:
                linked += 1
                cert_holder_data = {
                    'name': drug_obj.company.name,
                    'address': drug_obj.company.address,
                    'supp_type': 'Certificate Holder',
                    'updated_by': 'cmsman',
                }
                cert_holder_obj, created = Supplier.objects.get_or_create(
                    name=drug_obj.company.name,
                    defaults=cert_holder_data,
                    )
                if created:
                    new_suppliers += 1
                    print(f"\nAdded supplier: {cert_holder_obj.name}")
                    cmsitem.certificate_holder = cert_holder_obj
                    cmsitem.inventory_item_type = drugtype
                else:
                    sys.stdout.write('.')
        print(f"Processed: {processed}  |  Found linked: {linked}  |  New suppliers: {new_suppliers}")
