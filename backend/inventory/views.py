from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy, resolve, Resolver404
from django.db.models import Q, Sum
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse

from bootstrap_modal_forms.generic import (
    BSModalCreateView,
    BSModalReadView,
    BSModalUpdateView,
    BSModalDeleteView,
)
from .models import (
    Category,
    Item, ItemType,
    Vendor,
    DeliveryOrder,
    DeliveryItem,
)
from drugdb.models import RegisteredDrug
from cmsinv.models import InventoryItem, InventoryItemType
from .forms import (
    NewCategoryForm, CategoryUpdateForm,
    NewVendorForm, NewVendorModalForm, VendorUpdateForm, VendorUpdateModalForm,
    ItemUpdateModalForm, NewItemForm, NewItemModalForm,
    NewDeliveryOrderForm, NewDeliveryOrderModalForm, DeliveryOrderUpdateModalForm,
    DeliveryOrderAddDeliveryItemForm, DeliveryItemUpdateModalForm,
)
from django.utils import timezone

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
    item_type = ''
    category = ''
    status = ''

    def get_queryset(self):
        query = self.request.GET.get('q')
        self.item_type = self.request.GET.get('t') or ''
        self.category = self.request.GET.get('c') or ''
        self.status = self.request.GET.get('s') or ''
        if self.item_type:
            object_list = Item.objects.filter(
                item_type=ItemType.objects.get(value=self.item_type)
            ).order_by('name')
        else:
            object_list = Item.objects.all().order_by('name')
        if self.category:
            object_list = object_list.filter(
                category=Category.objects.get(value=self.category)
            )
        if self.status == '1':
            object_list = object_list.filter(is_active=True)
        elif self.status == '2':
            object_list = object_list.filter(is_active=False)
        if query:
            self.last_query = query
            object_list = object_list.filter(
                Q(name__icontains=query)|
                Q(reg_no__icontains=query) 
            ).order_by('is_active')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['item_type'] = self.item_type
        data['category'] = self.category
        data['status'] = self.status
        return data


class ItemDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details for item"""
    permission_required = ('inventory.view_item', )
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item_obj'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.object.cmsid:
            data['cmsitem_obj'] = InventoryItem.objects.get(id=self.object.cmsid) or None
        if self.object.reg_no:
            data['drug_obj'] = RegisteredDrug.objects.get(reg_no=self.object.reg_no) or None
        try:
            delivered_items = DeliveryItem.objects.filter(item__id=self.object.id)[:5]
        except DeliveryItem.DoesNotExist:
            delivered_items = None
        data['deliveryitem_obj_list'] = delivered_items
        return data


# class ItemUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
#     """Update details for item"""
#     permission_required = ('inventory.change_item', )
#     model = Item
#     form_class = ItemUpdateForm
#     template_name = 'inventory/item_update_form.html'

#     def get_success_url(self):
#         return reverse('inventory:ItemDetail', args=(self.object.pk,))

class ItemUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details for item"""
    permission_required = ('inventory.change_item', )
    model = Item
    form_class = ItemUpdateModalForm
    template_name = 'inventory/item_update_modal.html'
    next_url = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('next'):
            self.next_url = self.request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(ItemUpdateModal, self).get_form_kwargs()
        kwargs.update({
            'next_url': self.next_url,
            })
        return kwargs

    def get_success_url(self):
        try:
            resolve(self.next_url)
        except Resolver404:
            return reverse('inventory:ItemList')
        return self.next_url

class ItemDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete item"""
    permission_required = ('inventory.delete_item', )
    model = Item
    success_url = reverse_lazy('inventory:ItemList')


class NewItem(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item"""
    permission_required = ('inventory.add_item')
    template_name = 'inventory/new_item.html'
    form_class = NewItemForm
    success_message = 'Success: Item added'
    drug_obj = None
    vendor_obj = None
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('vendor'):
            self.vendor_obj = Vendor.objects.get(id=self.request.GET.get('vendor')) or None
        if self.request.GET.get('regno'):
            self.drug_obj = RegisteredDrug.objects.get(id=self.request.GET.get('regno')) or None
        self.next_url = self.request.GET.get('next') or None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.drug_obj:
            data['drug_obj'] = self.drug_obj
        if self.vendor_obj:
            data['vendor_obj'] = self.vendor_obj
        return data

    def get_success_url(self):
        try:
            resolve(self.next_url)
            return self.next_url
        except Resolver404: 
            return reverse('inventory:ItemList')
        return reverse('inventory:ItemList')

    def get_form_kwargs(self):
        kwargs = super(NewItem, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            'drug_obj': self.drug_obj,
            'next_url': self.next_url,
            })
        return kwargs

class NewItemModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new drug to items"""
    permission_required = ('inventory.add_item')
    template_name = 'inventory/new_item_modal.html'
    form_class = NewItemModalForm
    success_message = 'Success: Item added'
    drug_obj = None
    vendor_obj = None
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('vendor'):
            self.vendor_obj = Vendor.objects.get(id=self.request.GET.get('vendor')) or None
        if self.request.GET.get('regno'):
            self.drug_obj = RegisteredDrug.objects.get(id=self.request.GET.get('regno')) or None
        self.next_url = self.request.GET.get('next') or None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.drug_obj:
            data['drug_obj'] = self.drug_obj
        if self.vendor_obj:
            data['vendor_obj'] = self.vendor_obj
        return data

    def get_success_url(self):
        try:
            resolve(self.next_url)
            return self.next_url
        except Resolver404: 
            return reverse('inventory:ItemList')
        return reverse('inventory:ItemList')

    def get_form_kwargs(self):
        kwargs = super(NewItemModal, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            'drug_obj': self.drug_obj,
            'next_url': self.next_url,
            })
        return kwargs


# class NewItemFromVendor(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
#     """Add new item"""
#     permission_required = ('inventory.add_item', )
#     model = Item
#     form_class = NewItemFromVendorForm
#     template_name = 'inventory/new_item.html'
#     vendor_id = ''

#     def dispatch(self, request, *args, **kwargs):
#         if 'vendor_id' in kwargs:
#             self.vendor_id = kwargs['vendor_id']
#         else:
#             self.vendor_id = ''
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         if self.vendor_id:
#             data['vendor_id'] = self.vendor_id
#             vendor_obj = Vendor.objects.get(id=self.vendor_id)
#             data['vendor_name'] = vendor_obj.name
#         else:
#             data['vendor_name'] = ''
#         return data


class VendorList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List Vendors"""
    permission_required = ('inventory.view_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_list.html'
    context_object_name = 'vendor_list'
    paginate_by = 50
    last_query = ''
    last_query_count = 0
    suppliers_only = False

    def get_queryset(self):
        self.vtype = self.request.GET.get('vtype') or 'any'
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
        if self.vtype == 'supp':
            object_list = object_list.filter(is_supplier=True)
        elif self.vtype == 'misc':
            object_list = object_list.filter(is_supplier=False)
        self.last_query_count = object_list.count

        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['vtype'] = self.vtype
        return data

# class VendorSelectModal(ListView, LoginRequiredMixin, PermissionRequiredMixin):
#     """List Vendors"""
#     permission_required = ('inventory.view_vendor', )
#     model = Vendor
#     template_name = 'inventory/vendor_select_modal.html'
#     context_object_name = 'vendor_list'
#     paginate_by = 20
#     last_query = ''
#     last_query_count = 0
#     suppliers_only = False

#     def get_queryset(self):
#         self.vtype = self.request.GET.get('vtype') or 'supp'
#         query = self.request.GET.get('q')
#         if query:
#             self.last_query = query
#             object_list = Vendor.objects.filter(
#                 Q(name__icontains=query) |
#                 Q(alias__icontains=query)
#             )
#         else:
#             self.last_query = ''
#             object_list = Vendor.objects.all()
#         if self.vtype == 'supp':
#             object_list = object_list.filter(is_supplier=True)
#         elif self.vtype == 'misc':
#             object_list = object_list.filter(is_supplier=False)
#         self.last_query_count = object_list.count

#         return object_list

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['last_query'] = self.last_query
#         data['last_query_count'] = self.last_query_count
#         data['vtype'] = self.vtype
#         return data 

class VendorDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details for vendor"""
    permission_required = ('inventory.view_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_detail.html'
    context_object_name = 'vendor_obj'
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            self.object = Vendor.objects.get(id=kwargs['pk'])
        else:
            print("Error: missing pk")
        self.next_url = request.GET.get('next') or '/'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['vendor_obj'] = self.object
        try:
            delivered_items = DeliveryItem.objects.filter(delivery_order__vendor__id=self.object.id)[:20]
        except DeliveryItem.DoesNotExist:
            delivered_items = None
        data['deliveryitem_obj_list'] = delivered_items
        return data


class NewVendor(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new vendor"""
    permission_required = ('inventory.add_vendor', )
    model = Vendor
    template_name = 'inventory/new_vendor.html'
    form_class = NewVendorForm
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        self.next_url = request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(NewVendor, self).get_form_kwargs()
        kwargs.update({
            'next_url': self.next_url,
            })
        return kwargs

    def get_success_url(self):
        try:
            resolve(self.next_url)
        except Resolver404: 
            return reverse('inventory:VendorList')
        return f"{self.next_url}?vendor={self.object.pk}"


class NewVendorModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new vendor modal"""
    permission_required = ('inventory.add_vendor', )
    model = Vendor
    template_name = 'inventory/new_vendor_modal.html'
    form_class = NewVendorModalForm
    success_message = 'Success: Vendor was created.'
    
    def get_success_url(self):
        return f"{reverse('home')}?vendor={self.object.pk}"

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
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            self.object = Vendor.objects.get(id=kwargs['pk'])
        else:
            print("Error: missing pk")
        self.next_url = request.GET.get('next') or '/'
        print(self.next_url)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        try:
            resolve(self.next_url)
            return self.next_url
        except Resolver404: 
            return reverse('inventory:VendorList')

class VendorDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete vendor"""
    permission_required = ('inventory.delete_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_confirm_delete_modal.html'
    success_message = 'Success: Vendor deleted'
    success_url = reverse_lazy('inventory:VendorList')
    next_url = None

    def dispatch(self, request, *args, **kwargs):
        self.next_url = request.GET.get('next')
        print(self.next_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(NewVendor, self).get_form_kwargs()
        kwargs.update({
            'next_url': self.next_url,
            })
        return kwargs

    def get_success_url(self):
        try:
            resolve(self.next_url)
        except Resolver404: 
            return reverse('inventory:VendorList')
        return self.next_url


class DeliveryOrderList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists order deliveries
    """
    permission_required = ('inventory.view_deliveryorder', )
    template_name = 'inventory/deliveryorder_list.html'
    model = DeliveryOrder
    context_object_name = 'deliveryorder_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    disp_type = '1'

    def get_queryset(self):
        self.disp_type = self.request.GET.get('t')
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = DeliveryOrder.objects.filter(
                Q(vendor__name__icontains=query)
            ).order_by('-received_date')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = DeliveryOrder.objects.all().order_by('-received_date')
            self.last_query_count = object_list.count
        if self.disp_type == '1':  # Display unsynced records
            object_list = object_list.filter(
                cms_delivery_id__isnull=True
            )
        elif self.disp_type == '2':  # Display synced records
            object_list = object_list.exclude(cms_delivery_id__isnull=True)
        elif self.disp_type == '3':  # Display unpaid records
            object_list = object_list.filter(is_paid=False)
        elif self.disp_type == '4':  # Display paid records
            object_list = object_list.filter(is_paid=True)
        if self.begin:
            object_list = object_list.filter(received_date__gte=self.begin)
        if self.end:
            object_list = object_list.filter(received_date__lte=self.end)
        return object_list.order_by('-last_updated')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
        data['begin'] = self.begin
        data['end'] = self.end
        return data

class DeliveryOrderUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details of item delivery"""
    permission_required = ('inventory.change_deliveryorder', )
    model = DeliveryOrder
    form_class = DeliveryOrderUpdateModalForm
    template_name = 'inventory/deliveryorder_update_modal.html'
    vendor_obj = None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['deliveryorder_obj'] = self.object
        return data

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.object.pk,))


class DeliveryOrderDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete item delivery record"""
    permission_required = ('inventory.delete_deliveryorder', )
    model = DeliveryOrder
    template_name = 'inventory/deliveryorder_confirm_delete_modal.html'
    success_message = 'Success: Delivery Order deleted'
    success_url = reverse_lazy('inventory:DeliveryOrderList')


class NewDeliveryOrder(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item delivery"""
    permission_required = ('inventory.add_deliveryorder', )
    model = DeliveryOrder
    template_name = 'inventory/new_deliveryorder.html'
    form_class = NewDeliveryOrderForm
    vendor_obj = None

    def dispatch(self, request, *args, **kwargs):
        vendor_id = request.GET.get('vendor')
        if vendor_id:
            self.vendor_obj = Vendor.objects.get(id=vendor_id)
        else:
            self.vendor_obj = None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = timezone.now().strftime('%Y-%m-%d')
        data['vendor_obj'] = self.vendor_obj
        return data

    def get_form_kwargs(self):
        kwargs = super(NewDeliveryOrder, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            })
        return kwargs

    def get_success_url(self):
        
        return reverse('inventory:DeliveryOrderDetail', args=(self.object.pk,))

class NewDeliveryOrderModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item delivery"""
    permission_required = ('inventory.add_deliveryorder', )
    model = DeliveryOrder
    template_name = 'inventory/new_deliveryorder_modal.html'
    form_class = NewDeliveryOrderModalForm
    # context_object_name = 'new_deliveryorder'

    vendor_obj = None

    def dispatch(self, request, *args, **kwargs):
        vendor_id = request.GET.get('vendor')
        if vendor_id:
            self.vendor_obj = Vendor.objects.get(id=vendor_id)
        else:
            self.vendor_obj = None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = timezone.now().strftime('%Y-%m-%d')
        data['vendor_obj'] = self.vendor_obj
        return data

    def get_form_kwargs(self):
        kwargs = super(NewDeliveryOrderModal, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            })
        return kwargs

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.object.pk,))

# @login_required
# @permission_required('inventory.add_deliveryorder',)
# def NewDeliveryOrderSelectVendorView(request, *args, **kwargs):
#     """Select Vendor for New DeliveryOrder"""
#     vendors = Vendor.objects.all()
#     vendor_obj = None

#     MAX_QUERY_COUNT = 20
#     # Get query from request and search Vendor
#     vendor = request.GET.get('vendor')
#     if vendor:
#         vendor_obj = Vendor.objects.get(id=vendor)
#         query = None
#     else:
#         query = request.GET.get('q')
#     if query:
#         last_query = query
#         object_list = Vendor.objects.filter(Q(name__icontains=query))[:MAX_QUERY_COUNT]
#         last_query_count = object_list.count
#     else:
#         last_query = ''
#         object_list = Vendor.objects.all()[:MAX_QUERY_COUNT]
#         last_query_count = object_list.count
#     if request.is_ajax():
#         html = render_to_string(
#             template_name='inventory/_new_deliveryorder_choose_vendor.html',
#             context={
#                 'vendor_list': object_list,
#                 }
#         )
#         data_dict = {"html_from_view": html}
#         return JsonResponse(data=data_dict, safe=False)

#     return render(request, "inventory/new_deliveryorder_view.html", {'vendors': vendors, 'vendor_obj': vendor_obj})

@login_required
@permission_required('inventory.view_deliveryorder')
def DeliveryOrderDetail(request, *args, **kwargs):
    """Display summary plus add items"""
    MAX_QUERY_COUNT = 200

    # Parse delivery_id from request and get related objects
    delivery_obj = None
    if 'delivery_id' in kwargs:
        delivery_obj = DeliveryOrder.objects.get(id=kwargs['delivery_id'])
    ctx = {
        'delivery_obj': delivery_obj
    }

    # Get related DrugDelivery objects associated with delivery_id
    try:
        deliveryitems_list = delivery_obj.delivery_items.all()
    except:
        deliveryitems_list = None
    if deliveryitems_list:
        list_total = sum(round(lt.purchase_quantity * lt.unit_price * (1 - lt.discount/100), 2) for lt in deliveryitems_list)
        ctx['list_total'] = list_total
    else:
        ctx['list_total'] = 0
    ctx['deliveryitems_list'] = deliveryitems_list

    # Get query from request and search RegisteredDrug    
    query = request.GET.get('q')
    item_query = request.GET.get('iq')
    stype = request.GET.get('stype')
    if item_query:
        last_query = item_query
        object_list = Item.objects.filter(
            item_type=ItemType.objects.get(name='Consumable').id).filter(
            Q(name__icontains=item_query) 
        ).order_by('is_active')[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
        if request.is_ajax():
            html = render_to_string(
                template_name='inventory/_item_search_results_partial.html',
                context={
                    'item_list': object_list,
                    'delivery_id': delivery_obj.id,
                }
            )
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
    elif query:
        last_query = query
        if stype == 'regno':
            object_list = InventoryItem.objects.filter(
                Q(registration_no__icontains=query)
            ).order_by('discontinue')[:MAX_QUERY_COUNT]
        else:
            last_query = query
            object_list = InventoryItem.objects.filter(
                Q(alias__icontains=query) |
                Q(product_name__icontains=query) |
                # Q(generic_name__icontains=query) |
                Q(ingredient__icontains=query)
            ).order_by('discontinue')[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    else:
        last_query = ''
        object_list = InventoryItem.objects.all().order_by('discontinue')[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    if request.is_ajax():
        html = render_to_string(
            template_name='inventory/_drug_search_results_partial.html',
            context={
                'drug_list': object_list,
                'delivery_id': delivery_obj.id,
            }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "inventory/deliveryorder_detail.html", context=ctx)

class DeliveryItemUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update delivery order delivery item"""
    permission_required = ('inventory.change_deliveryorder', )
    model = DeliveryItem
    template_name = 'inventory/deliveryorder_deliveryitem_update_modal.html'
    form_class = DeliveryItemUpdateModalForm
    delivery_obj = None
    drug_obj = None
    success_message = 'Success: Delivery Item updated'

    def dispatch(self, request, *args, **kwargs):
        if 'delivery_id' in kwargs:
            self.delivery_obj = DeliveryOrder.objects.get(pk=kwargs['delivery_id'])
        else:
            print('error: no delivery_id')
        if 'pk' in kwargs:
            self.object = DeliveryItem.objects.get(pk=kwargs['pk'])
        self.drug_obj = InventoryItem.objects.get(pk=self.object.item.cmsid)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['listitem_obj'] = self.object
        data['drug_obj'] = self.drug_obj
        return data

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.delivery_obj.id,))

    def get_form_kwargs(self):
        kwargs = super(DeliveryItemUpdateModal, self).get_form_kwargs()
        kwargs.update({
            'delivery_obj': self.delivery_obj,
            })
        return kwargs

class DeliveryItemDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Expense modal"""
    permission_required = ('inventory.delete_deliveryitem',)
    model = DeliveryItem
    template_name = 'inventory/deliveryitem_confirm_delete_modal.html'
    success_message = 'Success: Delivery item was deleted.'
    delivery_obj = None

    def dispatch(self, request, *args, **kwargs):
        if 'delivery_id' in kwargs:
            self.delivery_obj = DeliveryOrder.objects.get(pk=kwargs['delivery_id'])
        else:
            print('No delivery_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['delivery_obj'] = self.delivery_obj
        return data

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.delivery_obj.id,))

# ****** Save for Update View
# @login_required
# @permission_required('inventory.add_deliveryorder', 'inventory.add_deliveryitem', 'cmsinv.view_inventoryitem', )
# def DeliveryOrderAddItemView(request, *args, **kwargs):
#     """Add Item and DeliveryItem to DeliveryOrder"""
    
#     # Get deliveryorder
#     if kwargs['delivery_id']:
#         delivery_obj = DeliveryOrder.objects.get(pk=kwargs['delivery_id'])
#     else:
#         delivery_obj = None
#         print("Error: no delivery_id")
#     if kwargs['cmsitem_id']:
#         drug_obj = InventoryItem.objects.get(pk=kwargs['cmsitem_id'])
#     # if request.method == 'GET':
#     #     reg_no = request.GET.get('reg_no')
#     # elif request.method == 'POST':
#     #     print(request.POST)
#     #     reg_no = request.POST.get('reg_no')
#     #     print(f"POST: reg_no - {reg_no}")
#     # else:
#     #     print("Invalid request method")
#     # if reg_no:
#     #     drug_obj = RegisteredDrug.objects.get(reg_no=reg_no)
#     #     print(f"Got {drug_obj.name}")
#     # else:
#     #     drug_obj = None

#     # Process form if POST, else render blank forms
#     if request.method == 'POST':
#         item_form = NewItemForm(request.POST)
#         deliveryitem_form = NewDeliveryItemForm(request.POST)

#         # Since DeliveryItem has a foreign key to Item, first need to validate and create new item
#         if item_form.is_valid():
#             print("Item form valid. Saving item")
#             print(deliveryitem_form) 
#             if deliveryitem_form.is_valid():
#                 print("Forms valid")
#                 # print(item_form.cleaned_data, deliveryitem_form.cleaned_data)
#                 # new_item = item_form.save()
#                 # deliveryitem_form.save()
#                 return HttpResponseRedirect(reverse('inventory:DeliveryOrderDetail', args=(delivery_obj.pk,)))
#             else:
#                 print("DeliveryItem form invalid")
#         else:
#             print("Invalid Item form")
#     else:
#         item_form = NewItemForm(drug_obj=drug_obj)
#         deliveryitem_form = NewDeliveryItemForm(delivery_obj=delivery_obj, drug_obj=drug_obj)
    
#     ctx = {
#         'form': item_form,
#         'form_2': deliveryitem_form,
#         'delivery_obj': delivery_obj,
#         'drug_obj': drug_obj,
#     }
#     return render(request, "inventory/deliveryorder_add_deliveryitem.html", ctx)

class DeliveryOrderAddDeliveryItem(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Add Item and DeliveryItem to DeliveryOrder"""
    permission_required = ('inventory.add_deliveryorder', 'inventory.add_deliveryitem')
    form_class = DeliveryOrderAddDeliveryItemForm
    model = DeliveryItem
    template_name = 'inventory/deliveryorder_add_deliveryitem.html'
    delivery_obj = None
    drug_obj = None
    reg_drug_obj = None
    item_obj = None
    success_message = 'Success: Drug added'

    def dispatch(self, request, *args, **kwargs):
        if kwargs['delivery_id']:
            self.delivery_obj = DeliveryOrder.objects.get(id=kwargs['delivery_id'])
            print(f"Got delivery { self.delivery_obj.id }")
        else:
            print('Error: no delivery_id')
        if request.GET.get('cmsid'):
            self.drug_obj = InventoryItem.objects.get(pk=request.GET.get('cmsid'))
            # Auto create/update item in case not already in database
            item_details = {
                'name': self.drug_obj.product_name,
                'cmsid': self.drug_obj.id,
                'reg_no': self.drug_obj.registration_no,
                'is_active': not self.drug_obj.discontinue,
            }
            self.item_obj, created = Item.objects.update_or_create(
                cmsid=self.drug_obj.id,
                defaults=item_details,
            )
            if created:
                print(f"Item {self.drug_obj.registration_no} | {self.drug_obj.product_name} not in database => created")
            else:
                print(f"Got item {self.drug_obj.id}")
        elif request.GET.get('item'):
            print(f"Request - item={request.GET.get('item')}")
            self.item_obj = Item.objects.get(id=request.GET.get('item'))
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        data = super().get_context_data(**kwargs)
        data['delivery_obj'] = self.delivery_obj
        data['drug_obj'] = self.drug_obj
        return data

    def get_form_kwargs(self):
        kwargs = super(DeliveryOrderAddDeliveryItem, self).get_form_kwargs()
        kwargs.update({
            'delivery_obj': self.delivery_obj,
            'drug_obj': self.drug_obj,
            'item_obj': self.item_obj, 
            })
        return kwargs

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.delivery_obj.pk,))

# @login_required
# @permission_required('inventory.view_deliveryorder')
# def ItemSelectDrugView(request, *args, **kwargs):
#     """Display summary plus add items"""
#     MAX_QUERY_COUNT = 50

#     # Get query from request and search RegisteredDrug    
#     query = request.GET.get('q')
#     print(f"q={query}")
#     if query:
#         last_query = query
#         object_list = RegisteredDrug.objects.filter(
#             Q(name__icontains=query) |
#             Q(reg_no__icontains=query) |
#             Q(ingredients__name__icontains=query)
#         )[:MAX_QUERY_COUNT]
#         last_query_count = object_list.count
#     else:
#         last_query = ''
#         object_list = RegisteredDrug.objects.all()[:MAX_QUERY_COUNT]
#         last_query_count = object_list.count
#     if request.is_ajax():
#         html = render_to_string(
#             template_name='inventory/_drug_search_results_partial.html',
#             context={
#                 'drug_list': object_list,
#                 }
#         )
#         data_dict = {"html_from_view": html}
#         return JsonResponse(data=data_dict, safe=False)

#     return render(request, "inventory/item_select_drug_view.html")


class DeliveryItemList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('inventory.view_deliveryitem',)
    template_name = 'inventory/deliveryorder_item_list.html'
    model = DeliveryItem
    context_object_name = 'deliveryitem_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    disp_type = '1'

    def get_queryset(self):
        self.disp_type = self.request.GET.get('t')
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = DeliveryItem.objects.filter(
                Q(item__name__icontains=query)|
                Q(item__reg_no__icontains=query)
            ).order_by('-delivery_order__invoice_date')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = DeliveryItem.objects.all().order_by('-delivery_order__invoice_date')
            self.last_query_count = object_list.count
        if self.begin:
            object_list = object_list.filter(delivery_order__invoice_date__gte=self.begin)
        if self.end:
            object_list = object_list.filter(delivery_order__invoice_date__lte=self.end)
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = timezone.now().strftime('%Y-%m-%d')
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
        data['begin'] = self.begin
        data['end'] = self.end
        return data
