import csv, os
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from ledger.models import Expense, ExpenseCategory, PaymentMethod
from inventory.models import Vendor
from django.conf import settings

class Command(BaseCommand):
    """
    Imports scraped drug list and parses data into respective models
    """
    help = 'Import .csv expense file'

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def append_record(self, line):
        """
        Takes line and splits items in the list into respective fields
        then creates records in the list

        Notes on import
        - [Category]: Number in first character parsed to respective ExpenseCategory
        - [Payee]: If Category=1, then Payee additionally added to Vendor
        - [InvoiceDate]:
        - [ExpectedDate]: Refers to date written on cheque
        >> Expense.entry_date: use ExpectedDate if a/v, otherwise InvoiceDate
        - [Amount]: in HKD; ignore row if Amount is 0
        - [ChequeNo]: Maps to Expense.payment_ref
        - [Remarks]: Maps to Description
        """
        expense_category_num = line[0][0]
        payee = line[1]
        invoice_date = line[2] if line[2] else None
        expected_date = line[3] if line[3] else None
        # Assign Entry date using expected date; otherwise invoice date
        entry_date = expected_date if expected_date else invoice_date
        amount = line[4]
        payment_ref = line[5]
        desc = line[6]
        payment_method_raw = line[7]
        today = date.today().strftime('%Y-%m-%d')
        other_ref = f"Imported on {today}"
        
        # Process Expense Category
        expense_category = ExpenseCategory.objects.filter(label__startswith=expense_category_num)[0]

        # Process Payee to Vendor 
        vendor = None

        SAVE_VENDOR_CATEGORIES = [
            '1',  # Drugs
            '3',  # Lab/Imaging
        ]
        if expense_category_num in SAVE_VENDOR_CATEGORIES:
            new_vendor = {
                'name': payee,
                'version': 1,
                'active': True,
                'updated_by': 'import'

            }
            vendor, created = Vendor.objects.get_or_create(
                name=payee,
                defaults=new_vendor
            )
            if created:
                self.stdout.write(f"Added vendor: {vendor.name} with id {vendor.id}")

        # Process Payment Method
        try:
            payment_method = PaymentMethod.objects.get(name=payment_method_raw)
        except:
            payment_method = PaymentMethod.objects.get(name='Other')
        
        # Add New Expense Entry
        new_expense = {
            'entry_date': entry_date,
            'amount': amount,
            'description': desc,
            'expected_date': expected_date,
            'invoice_date': invoice_date,
            'updated_by': 'import',
            'version': 1,
            'category': expense_category,
            'payee': payee,
            'vendor': vendor,
            'payment_method': payment_method,
            'payment_ref': payment_ref,
            'other_ref': other_ref,
        }

        self.stdout.write(f"Importing expense: {entry_date} | ${amount} to {payee}")
        exp = Expense(**new_expense)
        exp.save()
        
    def handle(self, *args, **options):
        DELIMITER = '|'
        EXPENSE_CSV_FILE = options['csvfile']
        filepath = os.path.join(settings.BASE_DIR, EXPENSE_CSV_FILE)
        self.stdout.write(f"Importing expenses from {filepath} using delimiter '{DELIMITER}'")

        lines = []
        try:
            with open(filepath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=DELIMITER)
                row = 0
                for line in csv_reader:
                    if row == 0:
                        # Skip header row
                        pass
                    else:
                        lines.append(line)
                        # self.stdout.write(f"[{row-1}] {DELIMITER.join(line)}")
                    row += 1
        except:
            self.stdout.write('Error reading .csv file')            
            return -1
        self.stdout.write(f"Number of records: {len(lines)}")
        self.stdout.write("====\nWriting to database:\n=====\n")
        for line in lines:
            self.append_record(line)

        
