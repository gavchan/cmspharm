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
    Assign associated Item to RegisteredDrug item if itemid exists
    """
    help = 'Assign associated Item to RegisteredDrug item if itemid exists'
    
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
                    record.item = None
                    record.save()
                    removed += 1
                if item:
                    if record.item == item:
                        sys.stdout.write("s")
                    else:
                        record.item = item
                        print(f"\nAssign item #{item.id} to {record}")
                        record.save()
                        fixed += 1
            sys.stdout.write(".")
        print(f"\nProcessed {count} registered drugs; fixed: {fixed}; removed items: {removed}")
        
        
