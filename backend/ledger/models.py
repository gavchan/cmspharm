from django.db import models
from django.urls import reverse
from datetime import date
from inventory.models import Vendor

class ExpenseCategory(models.Model):
    """
    Model definition for ExpenseCategory
    """
    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['label','-active']
        verbose_name = 'Expense category'
        verbose_name_plural = 'Expense categories'
    
    def __str__(self):
        return f"{self.label}"

class PaymentMethod(models.Model):
    """
    Model definition for PaymentMethod
    E.g. Cash, Cheque
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']
        verbose_name = 'Payment method'

    def __str__(self):
        return f"{self.name}"

class LedgerEntry(models.Model):
    """Base model definition for Ledger Entries"""

    entry_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    expected_date = models.DateField(verbose_name="Cheque/due date", blank=True, null=True)
    # expected_date: refers to due date (for income), cheque date (for cheque expense)
    settled_date = models.DateField(verbose_name="Settlement/paid date", blank=True, null=True)
    # settled_date: refers to the date payment deducted (cheque expense) or received
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-entry_date']
        verbose_name = 'Ledger entry'
        verbose_name_plural = 'Ledger entries'

    def __str__(self):
        return f"{self.entry_date} | ${self.amount} - {self.description}"

class Expense(LedgerEntry):
    """Model definition for Expense"""

    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT,
        blank=True, null=True
    )
    payee = models.CharField(max_length=255, blank=True, null=True)
    # vendor: can be the same as the payee; occasionally the payee name is different.
    vendor = models.ForeignKey(
        Vendor, blank=True, null=True,
        on_delete = models.PROTECT
        )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT,
    )
    # payment_ref: used for cheque number or other
    payment_ref = models.CharField(verbose_name="Cheque/ref no.", max_length=255, blank=True, null=True)
    invoice_no = models.CharField(max_length=255, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    other_ref = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-entry_date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def get_absolute_url(self):
        return reverse('ledger:ExpenseDetail', kwargs={'pk': self.pk})