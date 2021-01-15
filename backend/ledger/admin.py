from django.contrib import admin
from .models import (
    ExpenseCategory,
    PaymentMethod,
    Expense,
    IncomeCategory,
    IncomeSource,
)

admin.site.register(ExpenseCategory)
admin.site.register(PaymentMethod)
admin.site.register(Expense)
admin.site.register(IncomeCategory)
admin.site.register(IncomeSource)
# Register your models here.
