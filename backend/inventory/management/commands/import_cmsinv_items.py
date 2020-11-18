import csv, os, sys
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from cmsinv.models import InventoryItem
from drugdb.models import RegisteredDrug
from inventory.models import Item, ItemType, Category
from django.conf import settings

class Command(BaseCommand):
    """
    Imports CMS Inventory Items into inventory.Item
    """
    help = 'Imports CMS Inventory Items into inventory.Item'

    def run(self):
        """
        Iterate through CMS Inventory Item, create corresponding inventory.Item
        """

        cmsinv_items = InventoryItem.objects.all()
        item_type = ItemType.objects.get(value='1')
        category = Category.objects.get(value='1')
        count = 0
        for cmsinv_item in cmsinv_items:
            note = ''
            # Try get matching registered drug
            try:
                reg_drug = RegisteredDrug.objects.get(reg_no=cmsinv_item.registration_no)
            except RegisteredDrug.DoesNotExist:
                reg_drug = None
                note = 'No matching reg_no'
            item = {
                'name': cmsinv_item.product_name,
                'cmsid': cmsinv_item.id,
                'item_type': item_type,
                'category': category,
                'reg_no': cmsinv_item.registration_no,
                'note': note,
                'is_active': not cmsinv_item.discontinue,
            }
            new_item, created = Item.objects.update_or_create(cmsid=cmsinv_item.id, defaults=item)
            if created:
                count += 1
                self.stdout.write(f"Created id:{new_item.id} from cms:{cmsinv_item.id} | {cmsinv_item.product_name}")
            else:
                print(f"Update CMS {cmsinv_item.id} Reg # {cmsinv_item.registration_no}")
        print(f"Created {count} item records.")
        
    def handle(self, *args, **options):
        self.run()

        
