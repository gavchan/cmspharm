import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug
from inventory.models import Item, ItemType, Category
from cmsinv.models import InventoryItem, Supplier, InventoryItemType
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Fix Items - Check Item records for corresponding cmsid and reg_no
    """
    help = 'Fix Items - Check Item records for corresponding cmsid and reg_no'
        
    def add_arguments(self, parser):
        parser.add_argument('-c', '--create', action='store_true', help='Create CMS Inventory Item if missing')
        
    def handle(self, *args, **kwargs):
        create_missing_cmsitems = kwargs['create'] or False

        print("Checking existing Item records")
        # Check item
        missingCmsItems = []  # Missing CMS Items for Items that have Reg No (e.g. Delivered Items)
        for item in Item.objects.all():
            # Check CMS Inv Id
            missingCmsItem = False
            mismatchCmsid = False
            mismatchRegno = False
            message = ''
            sys.stdout.write(f"\nItem #{item.id}: ")
            if item.cmsid:
                try:
                    cmsitem = InventoryItem.objects.get(id=item.cmsid)
                except InventoryItem.DoesNotExist:
                    cmsitem = None
                if cmsitem:
                    sys.stdout.write(f"CMS[{cmsitem.id}] ")
                    # Try get reg drug from CMS InvItem
                    try:
                        regdrug = RegisteredDrug.objects.get(reg_no=cmsitem.registration_no.upper())
                    except:
                        regdrug = None
                    if regdrug:
                        sys.stdout.write(f"CMS_RegDrug[{regdrug.reg_no}]")
                        if item.reg_no == regdrug.reg_no:
                            sys.stdout.write(f" - Matches item reg_no. ")
                        else:
                            sys.stdout.write(f" - Does not match - to update item.reg_no. ")
                            item.reg_no = regdrug.reg_no
                            item.save()
                    else:
                        # CMSInvItem has reg_no, but no corresponding RegDrug
                        # May mean no longer registered
                        # To leave CMSInvItem reg_no intact, but item.reg_no should be set to None
                        if item.reg_no == None:
                            sys.stdout.write(f" - Item OK. ")
                        else:
                            item.reg_no = None
                            item.note = 'No matching reg_no. '
                            item.save()
                            message = f" - CMS id has no matching reg_no. Set reg_no=None. "
                else:
                    # If no matching CMS id, both cmsid and reg_no should be set as none.
                    mismatchCmsid = True
                    item.cmsid = None
                    item.reg_no = None
                    item.save()
            else:
                # No CMS Inventory Item for item.cmsid
                missingCmsItem = True
                
            # Check matching RegDrug
            if item.reg_no:
                try:
                    regdrug = RegisteredDrug.objects.get(reg_no=item.reg_no)
                except:
                    regdrug = None
                if regdrug:
                    sys.stdout.write(f"RegDrug[{regdrug.reg_no}]")
                    # If regdrug found, should expect corresponding CMSInvItem
                    if missingCmsItem:
                        missingCmsItems.append(regdrug.reg_no)
                        sys.stdout.write(f" - Missing CMS Inventory Item")
                else:
                    mismatchRegno = True
                    item.reg_no = None
                    item.save()
            if mismatchCmsid:
                sys.stdout.write(f"\nExpected CMS id {item.cmsid} - CMS InvItem not found; set to None")
            if mismatchRegno:
                sys.stdout.write(f"\nExpected RegDrug {item.reg_no} - RegDrug not found; set to None")
            if message:
                sys.stdout.write(message)

        print("\nThe following RegDrugs with Item entry are missing CMS InventoryItem:")
        print(missingCmsItems)
        if len(missingCmsItems) > 0 and create_missing_cmsitems:
            do_create = input("Create missing Inventory Items? Type 'YES' to continue: ")
            if do_create.upper() == "YES" or do_create.upper() == 'Y':
                for missingRegNo in missingCmsItems:
                    regdrug = RegisteredDrug.objects.get(reg_no=missingRegNo)
                    item = Item.objects.get(reg_no=missingRegNo)
                    drugItemType = InventoryItemType.objects.get(id=1)
                    # Check if existing cert_holder
                    cert_holder_data = {
                        'name': regdrug.company.name,
                        'address': regdrug.company.address,
                        'supp_type': 'Certificate Holder',
                        'updated_by': 'cmsman',
                    }
                    cert_holder_obj, created = Supplier.objects.get_or_create(
                        name=regdrug.company.name.upper(),
                        defaults=cert_holder_data,
                        )
                    if created:
                        print(f"Cert Holder created: {cert_holder_obj}")

                    newCmsInvItem = InventoryItem(
                        product_name=regdrug.name,
                        label_name=regdrug.name,
                        generic_name=regdrug.gen_generic,
                        alias='',
                        registration_no=regdrug.reg_no,
                        certificate_holder=cert_holder_obj,
                        ingredient=regdrug.ingredients_list,
                        inventory_type='Drug',
                        is_clinic_drug_list=True,
                        is_master_drug_list=True,
                        discontinue=False,
                        version=0,
                        updated_by='cmsman',
                        inventory_item_type=drugItemType,
                    )
                    newCmsInvItem.save()
                    if newCmsInvItem.id:
                        print(f"Created CMS Inv Item #{newCmsInvItem.id} for Drug {newCmsInvItem.registration_no}")
                        item.cmsid = newCmsInvItem.id
                        item.is_active = True
                        item.save()
                        print(f"Updated Item #{item.id} with CMS InvItem #{item.cmsid}")
                    else:
                        print(f"Error creating item for {regdrug.reg_no}")
            else:
                print("Aborting operation")
