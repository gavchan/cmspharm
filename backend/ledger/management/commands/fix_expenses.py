import csv, os
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from ledger.models import Expense
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
        - expected_date
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
        
    def handle(self, *args, **options):
        self.fix_expense_record()
        
