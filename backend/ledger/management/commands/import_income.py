import csv, os
import pandas as pd
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from ledger.models import Income, IncomeCategory, IncomeSource, PaymentMethod
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Imports scraped drug list and parses data into respective models
    """
    help = 'Import income .xlsx  file'

    def add_arguments(self, parser):
        parser.add_argument(
            "excelfile",
            help="The file system path to the Excel file with the data to import",
        )
        
    def handle(self, *args, **options):
        INCOME_XLSX_FILE = options['excelfile']
        filepath = os.path.join(settings.BASE_DIR, INCOME_XLSX_FILE)
        self.stdout.write(f"Importing income data from {filepath}")
        data = pd.read_excel(filepath)
        today =  timezone.now().strftime('%Y-%m-%d')
        # Get BankTx PaymentMethod
        methodBank = PaymentMethod.objects.get(name='Bank Tx')

        # Get/Create IncomeCategory
        categoryCard, created = IncomeCategory.objects.get_or_create(
            name='Medical Card',
            defaults={
                'name': 'Medical Card',
                'code': IncomeCategory.objects.all().count() + 1,
                'description': 'Medical Card Income',
                'active': True,
            })
        if created:
            print(f"Created 'Medical Card' IncomeCategory #{categoryCard.id}: {categoryCard.name}")

        for index, row in data.iterrows():
            print(f"Processing {index:3}|{row['Date']} - ${row['Amount']} from {row['Payer']}")
            payerData = {
                'name': row['Payer'],
                'code': IncomeSource.objects.all().count() + 1,
                'active': True
            }
            payer, created = IncomeSource.objects.get_or_create(name=row['Payer'], defaults=payerData)
            if created:
                print(f"Created payer #{payer.id}: {payer.name}")
            newIncome = Income(
                payer=payer,
                payment_method=methodBank,
                amount=row['Amount'],
                other_ref=row['Ref'],
                expected_date=row['Date'],
                entry_date = today,
                description='Service fees for period ' + str(row['Ref']),
                date_created = timezone.now(),
                last_updated = timezone.now(),
                updated_by = 'cmsman',
                version = 1,
            )
            newIncome.save()
            if newIncome.id:
                print(f"Created income #{newIncome.id}: ${newIncome.amount} from {newIncome.payer}")
            else:
                print(newIncome)
        
