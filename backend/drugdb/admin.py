from django.contrib import admin
from .models import RegisteredDrug, Company, DrugDelivery

admin.site.register(RegisteredDrug)
admin.site.register(Company)
admin.site.register(DrugDelivery)