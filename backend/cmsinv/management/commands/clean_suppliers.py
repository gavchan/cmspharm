import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug, Company, Ingredient
from cmsinv.models import (
    InventoryItem, Prescription, PrescriptionDetail, InventoryMovementLog,
    DepletionItem, ReceivedItem, Supplier, InventoryItemType, Delivery, ReceivedItem, InventoryItemSupplier,
    Request, RequestItem
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
        print("Deleting all records from Delivery, ReceivedItem, InventoryItemSupplier, Request, RequestItem")
        for record in ReceivedItem.objects.all():
            record.delete()
            sys.stdout.write('x')
        for record in Delivery.objects.all():
            record.delete()
            sys.stdout.write('x')
        for record in InventoryItemSupplier.objects.all():
            record.delete()
            sys.stdout.write('x')
        for record in RequestItem.objects.all():
            record.delete()
            sys.stdout.write('x')
        for record in Request.objects.all():
            record.delete()
            sys.stdout.write('x')
        print("\nReset all InventoryItems with valid reg_no - SupplierManufacturer to !_NA")
        NA = '!_NA'
        supplier_na = Supplier.objects.get(name=NA)
        processed = 0
        modified = 0
        supplierids_to_keep = set()
        for cmsitem in InventoryItem.objects.all():
            processed += 1
            try:
                drug_obj = RegisteredDrug.objects.get(reg_no=cmsitem.registration_no)
                cmsitem.certificate_holder = supplier_na
                cmsitem.save()
                sys.stdout.write('.')
                modified += 1
            except RegisteredDrug.DoesNotExist:
                drug_obj = None
                supplierids_to_keep.add(cmsitem.certificate_holder.id)
                sys.stdout.write('o')

        print(f"\nProcessed InventoryItems: {processed}  |  Modified: {modified}  | To Keep: {len(supplierids_to_keep)}")
        print(f"Keeping the following SupplierManufacturers: {supplierids_to_keep}")
        confirm_delete = input("Delete unused SupplierManufacturers? Type 'YES' or 'Y' to confirm delete and rebuild:")
        do_delete = confirm_delete.upper() == 'YES' or confirm_delete.upper() == 'Y'
        supplierids_to_keep.add(supplier_na.id)
        allsupplierids = set(supplier.id for supplier in Supplier.objects.all())
        supplierids_to_delete = allsupplierids.difference(supplierids_to_keep)
        deleted = 0
        for supplierid in supplierids_to_delete:
            supplier = Supplier.objects.get(id=supplierid)

            # Check if referenced in InventoryItem, if not then delete
            print(f"Cert Holder: {supplier.id} | {supplier.name}")
            try:
                testcmsitem = InventoryItem.objects.get(certificate_holder=supplier.id)
            except:
                testcmsitem = None
                if do_delete:
                    print(f"\nDelete {supplier.name}")
                    supplier.delete()
                    deleted += 1
                else:
                    print(f"\nNeed to delete {supplier.name}")
            if testcmsitem:
                print(f"{supplier.name} used by {testcmsitem.product_name}")
        print(f"\nDeleted SupplierManufacturers: {deleted}")

        if do_delete:
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
                        cmsitem.certificate_holder = cert_holder_obj.id
                        cmsitem.inventory_item_type = drugtype
                    else:
                        sys.stdout.write('.')
            print(f"Processed: {processed}  |  Found linked: {linked}  |  New suppliers: {new_suppliers}")
