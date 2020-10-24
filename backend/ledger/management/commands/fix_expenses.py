import csv, os
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from ledger.models import Expense, ExpenseCategory, PaymentMethod
from inventory.models import Vendor
from django.conf import settings

class Command(BaseCommand):
    """
    Fix missing invoice date / expected date from database
    """
    help = 'Fix missing invoice date / expected date from database'

    def fix_expense_record(self):
        """
        Iterate through expense records and set fix missing dates for
        - invoice_date
        - expected_date (to )

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

        expenses = Expense.objects.all()
        for record in expenses:
            replace = ''
            # Check invoice_date
            if record.invoice_date is None:
                print(f"Inv: {record.invoice_date} | Exp: {record.expected_date} | Settle: {record.settled_date} | Entry: {record.entry_date} | Remark: {record.remarks}")
                record.invoice_date = record.expected_date if record.expected_date else record.settled_date
                if record.invoice_date is None:
                    record.invoice_date = record.entry_date
                    replace = 'entry_date'
                else:
                    replace = 'expected_date'
                print(f"{record.id} invoice date set to {record.invoice_date}")
                remark = f"Missing invoice date set to {replace}"
                print(remark)

            if record.expected_date is None:
                print(f"Inv: {record.invoice_date} | Exp: {record.expected_date} | Settle: {record.settled_date} | Entry: {record.entry_date} | Remarks: {record.remarks}")
                record.expected_date = record.settled_date if record.settled_date else record.invoice_date
                if record.expected_date is None:
                    record.expected_date = record.entry_date
                    replace = 'entry_date'
                else:
                    replace = 'settled/invoice_date'
                print(f"{record.id} expected date set to {record.expected_date}")
                remark = f"Missing expected date set to {replace}"
                print(remark)
            
            record.save()

        # expense_category_num = line[0][0]
        # payee = line[1]
        # invoice_date = line[2] if line[2] else None
        # expected_date = line[3] if line[3] else None
        # # Assign Entry date using expected date; otherwise invoice date
        # entry_date = expected_date if expected_date else invoice_date
        # amount = line[4]
        # payment_ref = line[5]
        # desc = line[6]
        # payment_method_raw = line[7]
        # today = date.today().strftime('%Y-%m-%d')
        # other_ref = f"Imported on {today}"
        
        # # Process Expense Category
        # expense_category = ExpenseCategory.objects.filter(label__startswith=expense_category_num)[0]

        # # Process Payee to Vendor 
        # vendor = None

        # SAVE_VENDOR_CATEGORIES = [
        #     '1',  # Drugs
        #     '3',  # Lab/Imaging
        # ]
        # if expense_category_num in SAVE_VENDOR_CATEGORIES:
        #     new_vendor = {
        #         'name': payee,
        #         'version': 1,
        #         'active': True,
        #         'updated_by': 'import'

        #     }
        #     vendor, created = Vendor.objects.get_or_create(
        #         name=payee,
        #         defaults=new_vendor
        #     )
        #     if created:
        #         self.stdout.write(f"Added vendor: {vendor.name} with id {vendor.id}")

        # # Process Payment Method
        # try:
        #     payment_method = PaymentMethod.objects.get(name=payment_method_raw)
        # except:
        #     payment_method = PaymentMethod.objects.get(name='Other')
        
        # # Add New Expense Entry
        # new_expense = {
        #     'entry_date': entry_date,
        #     'amount': amount,
        #     'description': desc,
        #     'expected_date': expected_date,
        #     'invoice_date': invoice_date,
        #     'updated_by': 'import',
        #     'version': 1,
        #     'category': expense_category,
        #     'payee': payee,
        #     'vendor': vendor,
        #     'payment_method': payment_method,
        #     'payment_ref': payment_ref,
        #     'other_ref': other_ref,
        # }

        # self.stdout.write(f"Importing expense: {entry_date} | ${amount} to {payee}")
        # exp = Expense(**new_expense)
        # exp.save()
        
    def handle(self, *args, **options):
        self.fix_expense_record()
        
