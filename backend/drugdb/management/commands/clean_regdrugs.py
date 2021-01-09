import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug
from inventory.models import Item, ItemType, Category
from cmsinv.models import InventoryItem
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Cleans Registered Drugs - remove itemid if no longer in Item database
    """
    help = 'Cleans Registered Drugs - remove itemid if no longer in Item database'
    
    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', action='store_true', help='Force update')
        
    def handle(self, *args, **kwargs):
        force_flag = kwargs['force'] or False
        print("Checking for reference to missing item in Registered Drug records")
        count = 0
        fixed = 0
        removed = 0
        drugItemType = ItemType.objects.get(name="Drug")
        drugCategory = Category.objects.get(name="Drug")
        for record in RegisteredDrug.objects.all():
            count += 1

            # First remove any non-existing itemid
            if record.itemid:
                try:
                    item = Item.objects.get(pk=record.itemid)
                except Item.DoesNotExist:
                    item = None
                    print(f"\nItem #{record.itemid} does not exist. Removing itemid from {record}")
                    record.itemid = None     
                    record.save()
                    removed += 1
                sys.stdout.write(".")
        print(f"\nProcessed {count} registered drugs; fixed: {fixed}; removed items: {removed}")
        count = 0
        fixed = 0
        removed = 0
        sys.stdout.write(f"\nCheck if matching reg_no for CMS InvItem and Item exists. Force update={force_flag}\n")
        
        for record in RegisteredDrug.objects.all():
            # Check if matching reg_no exists
            try:
                cmsitem = InventoryItem.objects.get(registration_no=record.reg_no)
            except InventoryItem.DoesNotExist:
                cmsitem = None
            if cmsitem:
                # Found matching CMS InventoryItem, ensure Item matches record
                item_data = {
                    'name': record.name,
                    'cmsid': cmsitem.id,
                    'reg_no': record.reg_no,
                    'item_type': drugItemType,
                    'category': drugCategory,
                    'is_active': not cmsitem.discontinue,
                    'updated_by': 'cmsman'
                }
                item_update = False
                if force_flag:
                    item, created = Item.objects.update_or_create(reg_no=record.reg_no, defaults=item_data)
                    if not created:
                        print(f"\nUpdated item #{item.id} for {record}")
                else:
                    item, created = Item.objects.get_or_create(reg_no=record.reg_no, defaults=item_data)
                    # Only update if not matching cmsitem.id, reg_no
                    if not created:
                        if item.cmsid != cmsitem.id:
                            print(f"\nUnexpected: Item #{item.id} cmsid does not match CMSInvItem with reg_no {record.reg_no}")
                            item['name'] = record.name
                            item['cmsid'] = cmsitem.id
                            item['item_type'] = drugItemType
                            item['category'] = drugCategory
                            item['is_active'] = not cmsitem.discontinue
                            item['updated_by'] = 'cmsman'
                            item_update = True
                        if item_update:
                            item.save()
                            print(f"\nUpdated item #{item.id} for {record}")
                        else:
                            sys.stdout.write(".")

                if created:
                    print(f"\nCreated item #{item.id} for {record}")
                # Update RegDrug object
                record.itemid = item.id
                record.save()
                fixed += 1
            else:
                # No matching CMS InventoryItem
                if record.itemid:
                    print(f"\nUnexpected record.itemid={record.itemid}. Set as None")
                    record.itemid = None
                    record.save()
                    fixed += 1
                else:
                    # No associated item as no CMS InvItem - this is ok.
                    sys.stdout.write("o")
        print(f"\nProcessed {count} registered drugs; fixed: {fixed}; removed items: {removed}")
