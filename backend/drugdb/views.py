from django.views.generic import ListView
from django.db.models import Q
from .models import (
    RegisteredDrug,
    Company,
)

class RegisteredDrugList(ListView):
    """List of Registered Drugs"""
    template_name = 'drugdb/drug_list.html'
    model = RegisteredDrug
    context_object_name = 'drug_list'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            print(f"Query={query}")
            object_list = RegisteredDrug.objects.filter(
                Q(name__icontains=query) |
                Q(permit_no__icontains=query) |
                Q(ingredients__icontains=query)
            )
        else:
            print("Empty query")
            object_list = RegisteredDrug.objects.all()
        return object_list

class CompanyList(ListView):
    """List of Companies"""
    template_name = 'drugdb/company_list.html'
    model = Company
    context_object_name = 'company_list'
    paginate_by = 20

    def get_queryset(self):
        """Return 20 companies."""
        return Company.objects.all()