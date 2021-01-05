import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug, Company, Ingredient
from inventory.models import Item
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Cleans Registered Drugs - remove itemid if no longer in Item database
    """
    help = 'Cleans Registered Drugs - remove itemid if no longer in Item database'
        
    def handle(self, *args, **kwargs):

        print("Checking for missing itemid in Registered Drug records")
        count = 0
        fixed = 0
        for record in RegisteredDrug.objects.all():
            count += 1
            if record.itemid:
                try:
                    item = Item.objects.get(pk=record.itemid)
                except Item.DoesNotExist:
                    item = None
                    print(f"Item #{record.itemid} does not exist. Fixing {record}")
                    record.itemid = None     
                    record.save()
                    fixed += 1
                if item:
                    self.stdout.write(".")
            else:
                self.stdout.write(".")
            
        print(f"Processed {count} registered drugs; fixed: {fixed}")