from datetime import date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy, resolve, Resolver404
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.db.models import Q
from drugdb.models import (
    RegisteredDrug,
    Company,
)
from inventory.models import (
    Vendor,
    DeliveryItem,
)
from .models import (
    InventoryItem,
    Supplier,
)

from .forms import (
    NewInventoryItemForm,
    InventoryItemUpdateForm,
    InventoryItemMatchUpdateForm,
    InventoryItemQuickEditModalForm,
    SupplierQuickEditModalForm,
)

from bootstrap_modal_forms.generic import BSModalReadView, BSModalUpdateView

# InventoryItem Views
# ===================

class InventoryItemList(ListView, LoginRequiredMixin):
    """
    Lists drug deliveries
    """
    template_name = 'cmsinv/inventory_item_list.html'
    model = InventoryItem
    context_object_name = 'match_item_list_obj'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        print(f"query={query}")
        self.invtype = self.request.GET.get('invtype') or '1'
        self.status = self.request.GET.get('status') or '1'
        self.dd = self.request.GET.get('dd') or 'any'
        if query:
            self.last_query = query
            object_list = InventoryItem.objects.filter(
                Q(registration_no__icontains=query) |
                Q(product_name__icontains=query) |
                Q(generic_name__icontains=query) |
                Q(alias__icontains=query) |
                Q(clinic_drug_no__icontains=query) |
                Q(ingredient__icontains=query)
            ).order_by('discontinue')
        else:
            self.last_query = ''
            object_list = InventoryItem.objects.all().order_by('discontinue')
        if self.status == '1':
            object_list = object_list.filter(discontinue=False)
        elif self.status == '0':
            object_list = object_list.filter(discontinue=True)
        if self.invtype =='1':
            object_list = object_list.filter(inventory_type='Drug')
        elif self.invtype == '2':
            object_list = object_list.filter(inventory_type='Supplement')
        if self.dd == '1':
            object_list = object_list.filter(dangerous_sign=True)
        elif self.dd == '0':
            object_list = object_list.filter(dangerous_sign=False)
        self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['invtype'] = self.invtype
        data['status'] = self.status
        data['dd'] = self.dd
        return data

class InventoryItemDetail(DetailView, LoginRequiredMixin):
    """Display details of inventory item"""
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_detail.html'
    drug_obj = None
    deliveryitem_obj_list = None
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except RegisteredDrug.DoesNotExist:
            print("No registration no. for {self.object.product_name}")
        try:
            self.deliveryitem_obj_list = DeliveryItem.objects.filter(item__reg_no=self.object.registration_no)[:5]
        except DeliveryItem.DoesNotExist:
            self.deliveryitem_obj_list = None
            print(f"No delivery record for {self.object.product_name}")
        data['drug_obj'] = self.drug_obj
        data['deliveryitem_obj_list'] = self.deliveryitem_obj_list
        data['item_obj'] = self.object
        return data

class InventoryItemModalDetail(BSModalReadView, LoginRequiredMixin):
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_modal_detail.html'
    item_obj = None
    drug_obj = None
    drug_delivery_obj = None
    match_drug_list = None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except RegisteredDrug.DoesNotExist:
            print(f"No registration no. for {self.object.product_name}")
            # Try match name using first word of product name
            keyword = self.object.product_name.split()[0]
            self.match_drug_list = RegisteredDrug.objects.filter(Q(name__icontains=keyword))
        try:
            self.delivery_obj_list = DeliveryItem.objects.filter(item__reg_no=self.object.registration_no)[:5]
        except DeliveryItem.DoesNotExist:
            self.delivery_obj_list = None
            print(f"No delivery record for {self.object.product_name}")
        data['drug_obj'] = self.drug_obj
        data['delivery_obj_list'] = self.delivery_obj_list
        data['item_obj'] = self.object
        data['match_drug_list'] = self.match_drug_list
        return data

class InventoryItemQuickEditModal(BSModalUpdateView, LoginRequiredMixin):
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_quickedit_modal.html'
    form_class = InventoryItemQuickEditModalForm
    item_obj = None
    drug_obj = None
    match_drug_list = None
    set_match_drug = False
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            self.object = InventoryItem.objects.get(id=kwargs['pk'])
        else:
            print("Error: missing pk")
        self.item_obj = self.object
        self.next_url = request.GET.get('next') or None
        new_reg = self.request.GET.get('reg_no')
        if new_reg:
            self.set_match_drug = True
        try:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=self.item_obj.registration_no)
        except RegisteredDrug.DoesNotExist:
            print(f"No registration no. for {self.item_obj.product_name}")
            if self.set_match_drug:
                try:
                    self.drug_obj = RegisteredDrug.objects.get(reg_no=new_reg)
                except RegisteredDrug.DoesNotExist:
                    print(f"Error. No registration no. Expecting {new_reg}")
                if self.drug_obj:
                    print(f"Found {self.drug_obj.reg_no} | {self.drug_obj.name}")
            else:
                # Try match name using first word of product name
                keyword = self.item_obj.product_name.split()[0]
                self.match_drug_list = RegisteredDrug.objects.filter(Q(name__icontains=keyword))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        
        data['drug_obj'] = self.drug_obj
        data['item_obj'] = self.item_obj
        data['match_drug_list'] = self.match_drug_list
        data['set_match_drug'] = self.set_match_drug
        if self.drug_obj:
            data['generic_name'] = self.drug_obj.gen_generic
        data['next_clinic_no'] = InventoryItem.generateNextClinicDrugNo()
        return data

    def get_form_kwargs(self):
        kwargs = super(InventoryItemQuickEditModal, self).get_form_kwargs()
        kwargs.update({
            'drug_obj': self.drug_obj,
            'item_obj': self.item_obj,
            'set_match_drug': self.set_match_drug,
            })
        return kwargs

    def get_success_url(self):
        # return reverse('cmsinv:InventoryItemList')
        try:
            resolve(self.next_url)
            return self.next_url
        except Resolver404: 
            return reverse('cmsinv:InventoryItemList')

class InventoryItemUpdate(UpdateView, LoginRequiredMixin):
    """Update details of drug delivery"""
    model = InventoryItem
    form_class = InventoryItemUpdateForm
    template_name = 'cmsinv/inventory_item_update.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no) or None
        data['drug_obj'] = self.drug_obj
        data['item_obj'] = self.object
        data['next_clinic_no'] = InventoryItem.generateNextClinicDrugNo()
        return data

    def get_success_url(self):
        return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))

# class InventoryItemDelete(DeleteView, LoginRequiredMixin):
#     """Delete drug delivery record"""
#     model = InventoryItem
#     success_url = reverse_lazy('cmsinv:InventoryItemList')

class NewInventoryItem(CreateView, LoginRequiredMixin):
    """Add new drug delivery"""
    model = InventoryItem
    template_name = 'cmsinv/new_inventory_item.html'
    form_class = NewInventoryItemForm
    context_object_name = 'new_inventory_item'
    drug_reg_no = ''

    def dispatch(self, request, *args, **kwargs):
        if 'reg_no' in kwargs:
            self.drug_reg_no = kwargs['reg_no']
        else:
            self.drug_reg_no = ''
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.drug_reg_no:
            data['reg_no'] = self.drug_reg_no
            drug_obj = InventoryItem.objects.get(reg_no=self.drug_reg_no)
            data['product_name'] = drug_obj.name
            data['vendor'] = drug_obj.company
        else:
            print("Error: missing reg_no")
            data['product_name'] = ''
        return data

class MatchInventoryItemList(ListView, LoginRequiredMixin):
    """
    CMS Inventory Item List Matching Non-CMS Delivery Record
    """
    model = InventoryItem
    template_name = "cmsinv/match_inventory_item_list.html"
    context_object_name = 'match_item_list_obj'
    drug_reg_no = ''
    keyword = ''
    ingredients = ''
    drug_obj = None
    delivery_obj_list = None
    item_obj = None

    def dispatch(self, request, *args, **kwargs):
        if 'reg_no' in kwargs:
            self.drug_reg_no = kwargs['reg_no']
            try:
                self.item_obj = InventoryItem.objects.get(registration_no=self.drug_reg_no)
            except InventoryItem.DoesNotExist:
                self.item_obj = None
            try:
                self.drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
            except RegisteredDrug.DoesNotExist:
                self.drug_obj = None 
            try:
                self.delivery_obj_list = DeliveryItem.objects.filter(item__reg_no=self.drug_reg_no)[:5]
            except DeliveryItem.DoesNotExist:
                self.delivery_obj_list = None

        else:
            print("Error: missing reg_no")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['drug_obj'] =  self.drug_obj
        data['item_obj'] = self.item_obj
        print(data['drug_obj'])
        data['delivery_obj_list'] = self.delivery_obj_list
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

class InventoryItemMatchUpdate(UpdateView, LoginRequiredMixin):
    """
    CMS Inventory Item List Matching Non-CMS Delivery Record
    """
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_match_update.html'
    form_class = InventoryItemMatchUpdateForm
    item_obj = None
    drug_obj = None
    possible_drug_list = None
    delivery_obj = None
    delivery_obj_list = None
    
    def get_success_url(self):
        return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))
        
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except RegisteredDrug.DoesNotExist:
            print(f"No registration no. for {self.object.product_name}")
            
        try:
            self.delivery_obj_list = DeliveryItem.objects.filter(item__reg_no=self.object.registration_no).order_by('-delivery_order__received_date')[:5]
        except DeliveryItem.DoesNotExist:
            self.delivery_obj_list = None
            print(f"No delivery record for {self.object.product_name}")
        if self.delivery_obj_list:
            self.delivery_obj = self.delivery_obj_list[0]
        data['drug_obj'] = self.drug_obj
        data['delivery_obj'] = self.delivery_obj
        data['delivery_obj_list'] = self.delivery_obj_list
        data['item_obj'] = self.object
        return data

class SupplierList(ListView, LoginRequiredMixin):
    """
    Lists CMS suppliers
    """
    template_name = 'cmsinv/supplier_list.html'
    model = Supplier
    context_object_name = 'supplier_obj_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        print(f"query={query}")
        self.stype = self.request.GET.get('stype') or 'any'
        if query:
            self.last_query = query
            object_list = Supplier.objects.filter(
                name__icontains=query
            )
        else:
            self.last_query = ''
            object_list = Supplier.objects.all()
        if self.stype == 'cert':
            object_list = object_list.filter(supp_type='Certificate Holder')
        elif self.stype == 'supp':
            object_list = object_list.filter(supp_type='Supplier')
        elif self.stype == 'manf':
            object_list = object_list.filter(supp_type='Manufacturer')
        self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['stype'] = self.stype
        data
        return data

class SupplierQuickEditModal(BSModalUpdateView, LoginRequiredMixin):
    model = Supplier
    template_name = 'cmsinv/supplier_quickedit_modal.html'
    context_object_name = 'supplier_obj'
    form_class = SupplierQuickEditModalForm
    company_obj_list = None
    vendor_obj_list = None
   
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Search for similar names based on the first word in supplier name
        keyword = self.object.name.split()[0]
        if len(keyword) <=2:
            # Use first two word if first word is only 1-2 characters in length
            keyword = ' '.join(self.object.name.split()[:2])
        try:
            self.company_obj_list = Company.objects.filter(Q(name__icontains=keyword))
        except Company.DoesNotExist:
            print(f"No company for {keyword}")
        try:
            self.vendor_obj_list = Vendor.objects.filter(Q(name__icontains=keyword))
        except Vendor.DoesNotExist:
            print(f"No vendor for {keyword}")
        data['supplier_obj'] = self.object
        data['company_obj_list'] = self.company_obj_list
        data['vendor_obj_list'] = self.vendor_obj_list
        return data

    def get_form_kwargs(self):
        kwargs = super(SupplierQuickEditModal, self).get_form_kwargs()
        kwargs.update({
            'supplier_obj': self.object,
            })
        return kwargs

    def get_success_url(self):
        return reverse('cmsinv:SupplierList')
