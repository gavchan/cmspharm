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
    disp_type = ''

    def get_queryset(self):
        query = self.request.GET.get('q')
        if self.request.GET.get('t'):
            self.disp_type = self.request.GET.get('t')
        if self.disp_type == '1':   # Display unlinked
            object_list = RegisteredDrug.objects.filter(itemid=None)
        elif self.disp_type == '2':  # Display linked
            object_list = RegisteredDrug.objects.exclude(itemid=None)
        elif self.disp_type == '3':  # Display inactive
            object_list = RegisteredDrug.objects.filter(is_active=True)
        else:
            object_list = RegisteredDrug.objects.all()
        if query:
            self.last_query = query
            object_list = object_list.filter(
                Q(name__icontains=query) |
                Q(reg_no__icontains=query) |
                Q(ingredients__name__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
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
  
