from django.contrib import admin
from .models import RegisteredDrug, Company
from .custom_filters import DuplicateRegNoFilter

class RegisteredDrugAdmin(admin.ModelAdmin):
    list_filter = (DuplicateRegNoFilter, )

admin.site.register(RegisteredDrug, RegisteredDrugAdmin)
admin.site.register(Company)