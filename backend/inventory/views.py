from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from bootstrap_modal_forms.generic import (
    BSModalCreateView,
    BSModalUpdateView,
)
from .models import (
    Category,
    Item,
    Vendor,
    ItemDelivery,
)
from .forms import (
    NewCategoryForm, CategoryUpdateForm,
    NewVendorForm, NewVendorModalForm, VendorUpdateForm, VendorUpdateModalForm,
    NewItemForm, ItemUpdateForm,
    NewItemDeliveryForm, ItemDeliveryUpdateForm,
)


class CategoryList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List of inventory categories"""
    permission_required = ('inventory.view_category',)
    template_name = 'inventory/category_list.html'
    model = Category
    context_object_name = 'category_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = Category.objects.filter(
                Q(name__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = Category.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data


class NewCategory(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add category"""
    permission_required = ('inventory.add_category', )
    model = Category
    form_class = NewCategoryForm
    template_name = 'inventory/new_category.html'

# class NewCategory(BSModalCreateView, LoginRequiredMixin):
#     model = Category
#     form_class = NewCategoryModalForm
#     template_name = 'inventory/new_category_modal.html'

# class CategoryDetail(DetailView, LoginRequiredMixin):
#     """Display details for category"""
#     model = Category
#     template_name = 'inventory/category_detail.html'
#     context_object_name = 'category_detail'

#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)


class CategoryUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details for category"""
    permission_required = ('inventory.change_category', )
    model = Category
    form_class = CategoryUpdateForm
    template_name = 'inventory/category_update.html'
    success_url = reverse_lazy('inventory:CategoryList')

    # def get_success_url(self):
    #     return reverse('inventory:CategoryList')

class CategoryDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete category"""
    permission_required = ('inventory.delete_category')
    model = Category
    success_url = reverse_lazy('inventory:CategoryList')

class ItemList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List of inventory items"""
    permission_required = ('inventory.view_item', )
    template_name = 'inventory/item_list.html'
    model = Item
    context_object_name = 'item_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = Item.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = Item.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data


class ItemDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details for item"""
    permission_required = ('inventory.view_item', )
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item_detail'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)


class ItemUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details for item"""
    permission_required = ('inventory.change_item', )
    model = Item
    form_class = ItemUpdateForm
    template_name = 'inventory/item_update_form.html'

    def get_success_url(self):
        return reverse('inventory:ItemDetail', args=(self.object.pk,))


class ItemDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete item"""
    permission_required = ('inventory.delete_item', )
    model = Item
    success_url = reverse_lazy('inventory:ItemList')


class NewItem(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item"""
    permission_required = ('inventory.add_item', )
    model = Item
    form_class = NewItemForm
    template_name = 'inventory/new_item.html'
    vendor_id = ''

    def dispatch(self, request, *args, **kwargs):
        if 'vendor_id' in kwargs:
            self.vendor_id = kwargs['vendor_id']
        else:
            self.vendor_id = ''
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.vendor_id:
            data['vendor_id'] = self.vendor_id
            vendor_obj = Vendor.objects.get(id=self.vendor_id)
            data['vendor_name'] = vendor_obj.name
        else:
            data['vendor_name'] = ''
        return data


class VendorList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List of Vendors"""
    permission_required = ('inventory.view_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_list.html'
    context_object_name = 'vendor_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    suppliers_only = False

    def get_queryset(self):
        self.suppliers_only = self.request.GET.get('s')
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = Vendor.objects.filter(
                Q(name__icontains=query) |
                Q(alias__icontains=query)
            )
        else:
            self.last_query = ''
            object_list = Vendor.objects.all()
        if self.suppliers_only:
            object_list = object_list.filter(is_supplier=True)
        self.last_query_count = object_list.count

        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['suppliers_only'] = self.suppliers_only
        return data


class VendorDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details for vendor"""
    permission_required = ('inventory.view_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_detail.html'
    context_object_name = 'vendor_detail'


class NewVendor(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new vendor"""
    permission_required = ('inventory.add_vendor', )
    model = Vendor
    template_name = 'inventory/new_vendor.html'
    form_class = NewVendorForm
    success_url = reverse_lazy('inventory:VendorList')

class NewVendorModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new vendor modal"""
    permission_required = ('inventory.add_vendor', )
    model = Vendor
    template_name = 'inventory/new_vendor_modal.html'
    form_class = NewVendorModalForm
    success_message = 'Success: Vendor was created.'
    
    def get_success_url(self):
        return f"{reverse('ledger:NewExpense')}?vendor={self.object.pk}"

@csrf_exempt
def get_vendor_id(request):
    if request.is_ajax():
        vendor_name = request.GET['vendor_name']
        vendor_id = Vendor.objects.get(name=vendor_name).id
        data = {'vendor_id': vendor_id, }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")


class VendorUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details for vendor"""
    permission_required = ('inventory.change_vendor', )
    model = Vendor
    form_class = VendorUpdateForm
    template_name = 'inventory/vendor_update.html'
    success_url = reverse_lazy('inventory:VendorList')

class VendorUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update vendor details modal"""
    permission_required = ('inventory.change_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_update_modal.html'
    form_class = VendorUpdateModalForm
    success_message = 'Success: Vendor was updated.'

    def get_success_url(self):
        return reverse('inventory:VendorList')


class VendorDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete Vendor"""
    permission_required = ('inventory.delete_vendor', )
    model = Vendor
    success_url = reverse_lazy('inventory:VendorList')


class ItemDeliveryList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists item deliveries
    """
    permission_required = ('inventory.view_itemdelivery', )
    template_name = 'inventory/item_delivery_list.html'
    model = ItemDelivery
    context_object_name = 'item_delivery_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = ItemDelivery.objects.filter(
                Q(product_name__icontains=query) |
                Q(alias__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = ItemDelivery.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data


class ItemDeliveryDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details of item delivery"""
    permission_required = ('inventory.view_itemdelivery', )
    model = ItemDelivery
    template_name = 'inventory/item_delivery_detail.html'
    context_object_name = 'delivery_obj'


class ItemDeliveryUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details of item delivery"""
    permission_required = ('inventory.change_itemdelivery', )
    model = ItemDelivery
    form_class = ItemDeliveryUpdateForm
    template_name = 'inventory/item_delivery_update_form.html'

    def get_success_url(self):
        return reverse('inventory:ItemDeliveryDetail', args=(self.object.pk,))


class ItemDeliveryDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete item delivery record"""
    permission_required = ('inventory.delete_itemdelivery', )
    model = ItemDelivery
    success_url = reverse_lazy('inventory:ItemDeliveryList')


class NewItemDelivery(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item delivery"""
    permission_required = ('inventory.add_itemdelivery', )
    model = ItemDelivery
    template_name = 'inventory/new_item_delivery.html'
    form_class = NewItemDeliveryForm
    # context_object_name = 'new_item_delivery'
    item_id = ''

    def dispatch(self, request, *args, **kwargs):
        if 'item_id' in kwargs:
            self.item_id = kwargs['item_id']
        else:
            self.item_id = ''
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.item_id:
            data['item_id'] = self.item_id
            item_obj = Item.objects.get(id=self.item_id)
            data['item_name'] = item_obj.name
            data['item_vendor'] = item_obj.vendor
        else:
            print("Error: missing item id")
            data['item_name'] = ''
        return data

