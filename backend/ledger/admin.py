from django.contrib import admin
from .models import (
    ExpenseCategory,
    PaymentMethod,
    Expense,
)

admin.site.register(ExpenseCategory)
admin.site.register(PaymentMethod)
admin.site.register(Expense)
# Register your models here.
