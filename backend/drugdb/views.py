from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from ledger.models import (
    Expense,
)
from .models import (
    RegisteredDrug,
    Company,
)

class RegisteredDrugList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List of registered drugs"""
    permission_required = ('drugdb.view_registereddrug', )
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
                Q(reg_no__icontains=query) |
                Q(ingredients__name__icontains=query)
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

class RegisteredDrugDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details for registered drug"""
    permission_required = ('drugdb.view_registereddrug', )
    model = RegisteredDrug
    template_name = 'drugdb/drug_detail.html'
    context_object_name = 'drug_detail'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

class CompanyList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List of Companies"""
    permission_required = ('drugdb.view_company', )
    template_name = 'drugdb/company_list.html'
    model = Company
    context_object_name = 'company_list'
    paginate_by = 20

    def get_queryset(self):
        return Company.objects.all()
  
