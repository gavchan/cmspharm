import csv, os
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from drugdb.models import DrugDelivery
from django.conf import settings

class Command(BaseCommand):
    """
    Convert expiry_date to expiry_month
    """
    help = 'Convert expiry_date to expiry_month for existing records'

    def run(self):
        """
        Iterate through drug delivery records and convert expiry_date to expiry_month
        """

        records = DrugDelivery.objects.all()
        count = 0
        for record in records:
            # Check expiry_date, to convert to expiry_month if exists
            if record.expiry_date is not None:
                replace = record.expiry_date.strftime("%Y%m")
                print(f"Convert expiry_date: {record.expiry_date} => {replace}")
                count += 1
            else:
                replace = ''

            record.expiry_month = replace
            record.save()
        print(f"Converted {count} records.")
        
    def handle(self, *args, **options):
        self.run()

        
