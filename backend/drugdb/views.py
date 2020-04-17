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
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = RegisteredDrug.objects.filter(
                Q(name__icontains=query) |
                Q(permit_no__icontains=query) |
                Q(ingredients__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = RegisteredDrug.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data

class CompanyList(ListView):
    """List of Companies"""
    template_name = 'drugdb/company_list.html'
    model = Company
    context_object_name = 'company_list'
    paginate_by = 20

    def get_queryset(self):
        return Company.objects.all()