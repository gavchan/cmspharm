from datetime import date
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from drugdb.models import (
    RegisteredDrug,
    DrugDelivery,
)
from .models import (
    InventoryItem,
)

from .forms import (
    InventoryItemUpdateForm
)

from bootstrap_modal_forms.generic import BSModalReadView

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
        if query:
            self.last_query = query
            object_list = InventoryItem.objects.filter(
                Q(registration_no__icontains=query) |
                Q(product_name__icontains=query) |
                Q(alias__icontains=query) |
                Q(clinic_drug_no__icontains=query) |
                Q(ingredient__icontains=query)
            ).order_by('discontinue', 'product_name')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = InventoryItem.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['next_clinic_drug_no'] = InventoryItem.generateNextClinicDrugNo()
        return data

class InventoryItemDetail(DetailView, LoginRequiredMixin):
    """Display details of inventory item"""
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_detail.html'
    context_object_name = 'item_obj'
    drug_reg_no = ''
    keyword = ''
    ingredients = ''
    reg_drug_obj = None
    drug_delivery_obj = None
    reg_match_obj = None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.reg_drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except RegisteredDrug.DoesNotExist:
            print("No registration no. for {self.object.product_name}")
        try:
            self.drug_delivery_obj = DrugDelivery.objects.get(reg_no=self.object.registration_no)
        except DrugDelivery.DoesNotExist:
            print("No delivery record for {self.object.product_name}")
        data['reg_drug_obj'] = self.reg_drug_obj
        data['drug_delivery_obj'] = self.drug_delivery_obj
        return data

class InventoryItemModalDetail(BSModalReadView, LoginRequiredMixin):
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_modal_detail.html'
    item_obj = None
    reg_drug_obj = None
    drug_delivery_obj = None
   
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['reg_drug_obj'] =  self.reg_drug_obj
        data['item_obj'] = self.object
        print(data['reg_drug_obj'])
        data['delivery_obj_list'] = self.delivery_obj_list
        return data

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.reg_drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except RegisteredDrug.DoesNotExist:
            print("No registration no. for {self.object.product_name}")
        try:
            self.delivery_obj_list = DrugDelivery.objects.filter(reg_no=self.object.registration_no)[:5]
        except DrugDelivery.DoesNotExist:
            self.delivery_obj_list = None
            print(f"No delivery record for {self.object.product_name}")
        data['reg_drug_obj'] = self.reg_drug_obj
        data['delivery_obj_list'] = self.delivery_obj_list
        data['item_obj'] = self.object
        return data

class InventoryItemUpdate(UpdateView, LoginRequiredMixin):
    """Update details of drug delivery"""
    model = InventoryItem
    form_class = InventoryItemUpdateForm
    template_name = 'cmsinv/inventory_item_update.html'

    def get_success_url(self):
        return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))

# class InventoryItemDelete(DeleteView, LoginRequiredMixin):
#     """Delete drug delivery record"""
#     model = InventoryItem
#     success_url = reverse_lazy('cmsinv:InventoryItemList')

# class NewInventoryItem(CreateView, LoginRequiredMixin):
#     """Add new drug delivery"""
#     model = InventoryItem
#     template_name = 'cmsinv/new_inventory_item.html'
#     form_class = NewInventoryItemForm
#     context_object_name = 'new_inventory_item'
#     drug_reg_no = ''

#     def dispatch(self, request, *args, **kwargs):
#         if 'reg_no' in kwargs:
#             self.drug_reg_no = kwargs['reg_no']
#         else:
#             self.drug_reg_no = ''
#         return super().dispatch(request, *args, **kwargs)
    
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         if self.drug_reg_no:
#             data['reg_no'] = self.drug_reg_no
#             drug_obj = InventoryItem.objects.get(reg_no=self.drug_reg_no)
#             data['product_name'] = drug_obj.name
#             data['vendor'] = drug_obj.company
#         else:
#             print("Error: missing reg_no")
#             data['product_name'] = ''
#         return data

class MatchDeliveryInventoryItemList(ListView, LoginRequiredMixin):
    model = InventoryItem
    template_name = "cmsinv/match_delivery_inventory_item_list.html"
    context_object_name = 'match_item_list_obj'
    drug_delivery_obj = None
    reg_drug_obj = None
    reg_match_obj = None

    def dispatch(self, request, *args, **kwargs):
        if 'delivery_id' in kwargs:
            self.drug_delivery_obj = DrugDelivery.objects.get(id=kwargs['delivery_id'])
            self.reg_drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_delivery_obj.reg_no)
            self.reg_match_obj = InventoryItem.objects.get(registration_no=self.drug_delivery_obj.reg_no)
        else:
            print("Error: missing delivery_id")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['drug_delivery_obj'] =  self.drug_delivery_obj
        data['reg_drug_obj'] = self.reg_drug_obj
        data['reg_match_obj'] = self.reg_match_obj
        return data

    def get_queryset(self):
        keyword = self.reg_drug_obj.name.split(' ')[0]
        object_list = InventoryItem.objects.filter(
            Q(product_name__icontains=keyword) |
            Q(generic_name__icontains=keyword) |
            Q(alias__icontains=keyword) |
            Q(ingredient__icontains=self.reg_drug_obj.ingredients)
        ).exclude(registration_no=self.drug_delivery_obj.reg_no)[:100]
        return object_list

class MatchInventoryItemList(ListView, LoginRequiredMixin):
    model = InventoryItem
    template_name = "cmsinv/match_inventory_item_list.html"
    context_object_name = 'match_item_list_obj'
    drug_reg_no = ''
    keyword = ''
    ingredients = ''
    reg_drug_obj = None
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
                self.reg_drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
            except RegisteredDrug.DoesNotExist:
                self.reg_drug_obj = None 
            try:
                self.delivery_obj_list = DrugDelivery.objects.filter(reg_no=self.drug_reg_no)[:5]
            except DrugDelivery.DoesNotExist:
                self.delivery_obj_list = None

        else:
            print("Error: missing reg_no")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['reg_drug_obj'] =  self.reg_drug_obj
        data['item_obj'] = self.item_obj
        print(data['reg_drug_obj'])
        data['delivery_obj_list'] = self.delivery_obj_list
        return data

    def get_queryset(self):
        if self.reg_drug_obj:
            print('Should be existing reg drug no.')
            self.keyword = self.reg_drug_obj.name
            self.ingredients = self.reg_drug_obj.ingredients
        else:
            print('Error no existing reg no.')
        if self.keyword == None:
            self.keyword = ''
        if self.ingredients == None:
            self.ingredients = ''
        print(f"Filter for: { self.keyword }; {self.ingredients }")    
        object_list = InventoryItem.objects.filter(
            Q(product_name__icontains=self.keyword) |
            Q(generic_name__icontains=self.keyword) |
            Q(alias__icontains=self.keyword) |
            Q(ingredient__icontains=self.ingredients)
        ).order_by('discontinue').exclude(registration_no=self.drug_reg_no)[:100]
        return object_list