from django.contrib import admin
from .models import RegisteredDrug, Company, DrugUnit 

admin.site.register(RegisteredDrug)
admin.site.register(Company)
admin.site.register(DrugUnit)