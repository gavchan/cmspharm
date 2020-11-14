import csv, os, sys
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug
from cmsinv.models import InventoryItem
from django.conf import settings

class Command(BaseCommand):
    """
    Matches CMS Inventory Item with Registered Drug via registration no.
    """
    help = 'Matches CMS Inventory Item with Registered Drug via registration no.'

    def run(self):
        """
        Iterate through registered drug records and add matching CMS Inventory Item
        """

        records = RegisteredDrug.objects.all()
        count = 0
        for record in records:
            # Check for matching registration no. in CMS Inventory
            try:
                match = InventoryItem.objects.get(registration_no=record.reg_no)
            except InventoryItem.DoesNotExist:
                sys.stdout.write('.')
                continue
            if match:
                count += 1
                records.cmsinv_item = match.id
                match.inventory_type = 'Drug'
                print(f"Matched {record.reg_no} to CMS {match.id:6} | {match.product_name}")
                match.save()
                record.save()
        print(f"Matched {count} records.")
        
    def handle(self, *args, **options):
        self.run()

        
