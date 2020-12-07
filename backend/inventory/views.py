from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
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
    Item,
    Vendor,
    DeliveryOrder,
    DeliveryItem,
)
from drugdb.models import RegisteredDrug
from cmsinv.models import InventoryItem, InventoryItemType
from .forms import (
    NewCategoryForm, CategoryUpdateForm,
    NewVendorForm, NewVendorModalForm, VendorUpdateForm, VendorUpdateModalForm,
    NewItemModalForm, NewItemFromVendorForm, ItemUpdateForm,
    NewDeliveryOrderModalForm, DeliveryOrderUpdateModalForm,
    DeliveryOrderAddDeliveryItemForm, DeliveryItemUpdateModalForm,
)
from datetime import date

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
                Q(name__icontains=query) 
            ).order_by('-is_active','name')
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


class NewItemFromVendor(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new item"""
    permission_required = ('inventory.add_item', )
    model = Item
    form_class = NewItemFromVendorForm
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

class VendorSelectModal(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """List Vendors"""
    permission_required = ('inventory.view_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_select_modal.html'
    context_object_name = 'vendor_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    suppliers_only = False

    def get_queryset(self):
        self.vtype = self.request.GET.get('vtype') or 'supp'
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

    def get_success_url(self):
        return f"{reverse('home')}?vendor={self.object.pk}"

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

    def get_success_url(self):
        return reverse('inventory:VendorList')


class VendorDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete vendor"""
    permission_required = ('inventory.delete_vendor', )
    model = Vendor
    template_name = 'inventory/vendor_confirm_delete_modal.html'
    success_message = 'Success: Vendor deleted'
    success_url = reverse_lazy('inventory:VendorList')


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
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = DeliveryOrder.objects.filter(
                Q(vendor__name__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = DeliveryOrder.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
        return data

class DeliveryOrderUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details of item delivery"""
    permission_required = ('inventory.change_deliveryorder', )
    model = DeliveryOrder
    form_class = DeliveryOrderUpdateModalForm
    template_name = 'inventory/deliveryorder_update_modal.html'
    vendor_obj = None

    def get_success_url(self):
        return reverse('inventory:DeliveryOrderDetail', args=(self.object.pk,))


class DeliveryOrderDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete item delivery record"""
    permission_required = ('inventory.delete_deliveryorder', )
    model = DeliveryOrder
    template_name = 'inventory/deliveryorder_confirm_delete_modal.html'
    success_message = 'Success: Delivery Order deleted'
    success_url = reverse_lazy('inventory:DeliveryOrderList')


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
        data['today'] = date.today().strftime('%Y-%m-%d')
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

@login_required
@permission_required('inventory.add_deliveryorder',)
def NewDeliveryOrderSelectVendorView(request, *args, **kwargs):
    """Select Vendor for New DeliveryOrder"""
    vendors = Vendor.objects.all()
    vendor_obj = None

    MAX_QUERY_COUNT = 20
    # Get query from request and search Vendor
    vendor = request.GET.get('vendor')
    if vendor:
        vendor_obj = Vendor.objects.get(id=vendor)
        query = None
    else:
        query = request.GET.get('q')
    if query:
        last_query = query
        object_list = Vendor.objects.filter(Q(name__icontains=query))[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    else:
        last_query = ''
        object_list = Vendor.objects.all()[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    if request.is_ajax():
        html = render_to_string(
            template_name='inventory/_new_deliveryorder_choose_vendor.html',
            context={
                'vendor_list': object_list,
                }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "inventory/new_deliveryorder_view.html", {'vendors': vendors, 'vendor_obj': vendor_obj})

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
    if query:
        last_query = query
        object_list = InventoryItem.objects.filter(
            Q(alias__icontains=query) |
            Q(registration_no__icontains=query) |
            Q(product_name__icontains=query) |
            Q(generic_name__icontains=query) |
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
        if 'delivery_id' in kwargs:
            self.delivery_obj = DeliveryOrder.objects.get(id=kwargs['delivery_id'])
        else:
            print('Error: no delivery_id')
        if kwargs['cmsitem_id']:
            self.drug_obj = InventoryItem.objects.get(pk=kwargs['cmsitem_id'])
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
            print('Error: no cmsitem_id')
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

@login_required
@permission_required('inventory.view_deliveryorder')
def ItemSelectDrugView(request, *args, **kwargs):
    """Display summary plus add items"""
    MAX_QUERY_COUNT = 50

    # Get query from request and search RegisteredDrug    
    query = request.GET.get('q')
    print(f"q={query}")
    if query:
        last_query = query
        object_list = RegisteredDrug.objects.filter(
            Q(name__icontains=query) |
            Q(reg_no__icontains=query) |
            Q(ingredients__name__icontains=query)
        )[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    else:
        last_query = ''
        object_list = RegisteredDrug.objects.all()[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    if request.is_ajax():
        html = render_to_string(
            template_name='inventory/_drug_search_results_partial.html',
            context={
                'drug_list': object_list,
                }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "inventory/item_select_drug_view.html")


class NewItemModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new drug to items"""
    permission_required = ('inventory.add_item')
    template_name = 'inventory/new_item_modal.html'
    form_class = NewItemModalForm
    drug_obj = None
    success_message = 'Success: Drug added'

    def dispatch(self, request, *args, **kwargs):
       if 'drug_id' in kwargs:
            self.drug_obj = RegisteredDrug.objects.get(id=kwargs['drug_id'])
            print(f"Retrieved {self.drug_obj}")
       return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.drug_obj:
            data['drug_obj'] = self.drug_obj
        return data

    def get_success_url(self):
        return reverse('inventory:ItemList')

    def get_form_kwargs(self):
        kwargs = super(NewItemModal, self).get_form_kwargs()
        kwargs.update({
            'drug_obj': self.drug_obj,
            })
        print(kwargs)
        return kwargs


class ItemUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details for item"""
    permission_required = ('inventory.change_item', )
    model = Item
    form_class = NewItemModalForm
    template_name = 'inventory/item_update_form.html'

    def get_success_url(self):
        return reverse('inventory:ItemDetail', args=(self.object.pk,))

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
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = DeliveryItem.objects.all()
            filter(
                Q(item_name__icontains=query)|
                Q(item_reg_no__icontains=query)
            ).order_by('-delivery_order__received_date')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = DeliveryItem.objects.all().order_by('-delivery_order__received_date')
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = date.today().strftime('%Y-%m-%d')
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
        return data


        