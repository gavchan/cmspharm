from django.contrib import admin
from .models import Bill, BillDetail, Cashbook, ChargeItem

admin.site.register(Bill)
admin.site.register(BillDetail)
admin.site.register(Cashbook)
admin.site.register(ChargeItem)