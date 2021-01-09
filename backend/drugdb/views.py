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

from cmsinv.models import (
    InventoryItem
)

from inventory.models import (
    Item, DeliveryItem
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
        return object_list.distinct().order_by('name')

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
  
class DrugDetailMatch(ListView, LoginRequiredMixin):
    """
    CMS Inventory Item List Matching Non-CMS Delivery Record
    """
    model = InventoryItem
    template_name = "drugdb/drug_detail_match.html"
    context_object_name = 'match_item_list_obj'
    drug_reg_no = ''
    keyword = ''
    ingredients = ''
    drug_obj = None
    deliveryitem_obj_list = None
    cmsitem_obj = None
    item_obj = None

    def dispatch(self, request, *args, **kwargs):
        if 'reg_no' in kwargs:
            self.drug_reg_no = kwargs['reg_no']
            try:
                self.cmsitem_obj = InventoryItem.objects.get(registration_no=self.drug_reg_no)
            except InventoryItem.DoesNotExist:
                self.cmsitem_obj = None
            try:
                self.item_obj = Item.objects.get(reg_no=self.drug_reg_no)
            except Item.DoesNotExist:
                self.item_obj = None
            try:
                self.drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
            except RegisteredDrug.DoesNotExist:
                self.drug_obj = None 
            try:
                self.deliveryitem_obj_list = DeliveryItem.objects.filter(item__reg_no=self.drug_reg_no)[:5]
            except DeliveryItem.DoesNotExist:
                self.deliveryitem_obj_list = None
        else:
            print("Error: missing reg_no")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['drug_obj'] =  self.drug_obj
        data['cmsitem_obj'] = self.cmsitem_obj
        data['item_obj'] = self.item_obj
        data['deliveryitem_obj_list'] = self.deliveryitem_obj_list
        return data

    def get_queryset(self):
        if self.drug_obj:
            self.keyword = self.drug_obj.name
            self.ingredients = self.drug_obj.ingredients_list
        else:
            print('Error no existing reg no.')
        if self.keyword == None:
            self.keyword = ''
        if self.ingredients == None:
            self.ingredients = ''
        object_list = InventoryItem.objects.filter(
            Q(product_name__icontains=self.keyword) |
            Q(generic_name__icontains=self.keyword) |
            Q(alias__icontains=self.keyword) |
            Q(ingredient__icontains=self.ingredients)
        ).order_by('discontinue').exclude(registration_no=self.drug_reg_no)[:100]
        return object_list
