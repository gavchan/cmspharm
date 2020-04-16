from django.views import generic
#from django.shortcuts import get_object_or_404, render
from .models import (
    RegisteredDrug,
    Company,
)

class RegisteredDrugList(generic.ListView):
    template_name = 'drugdb/drug_list.html'
    model = RegisteredDrug
    context_object_name = 'drug_list'

    def get_queryset(self):
        """Return 20 drugs."""
        return RegisteredDrug.objects.all()[:20]

class CompanyList(generic.ListView):
    template_name = 'drugdb/company_list.html'
    model = Company
    context_object_name = 'company_list'

    def get_queryset(self):
        """Return 20 companies."""
        return Company.objects.all()[:20]