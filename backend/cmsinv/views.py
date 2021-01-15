from datetime import datetime
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy, resolve, Resolver404
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.db.models import Q
from drugdb.models import (
    RegisteredDrug,
    Company,
)
from inventory.models import (
    Vendor,
    DeliveryOrder,
    DeliveryItem,
    Item, ItemType,
)
from cmssys.models import (
    CmsUser,
    AuditLog,
)
from .models import (
    InventoryItem,
    InventoryItemType,
    Supplier,
    InventoryMovementLog,
    Delivery,
    ReceivedItem,
)

from .forms import (
    NewInventoryItemForm,
    InventoryItemUpdateForm,
    InventoryItemMatchUpdateForm,
    InventoryItemQuickEditModalForm,
    SupplierQuickEditModalForm,
    # NewDeliveryFromDeliveryOrderModalForm,
)

from bootstrap_modal_forms.generic import BSModalReadView, BSModalUpdateView, BSModalCreateView

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
        self.invtype = self.request.GET.get('invtype') or '1'
        self.status = self.request.GET.get('status') or ''
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
            self.drug_obj = None
        try:
            self.deliveryitem_obj_list = DeliveryItem.objects.filter(item__cmsid=self.object.id)[:10]
        except DeliveryItem.DoesNotExist:
            self.deliveryitem_obj_list = None
            # print(f"No delivery record for {self.object.product_name}")
        # Try get first 3 ingredients from CMS Item
        if self.object.ingredient:
            try:
                related_words = self.object.ingredient.split(',')
            except:
                related_words = []
        else:
            # If no ingredient, try product_name
            try:
                related_words = self.object.product_name.split(' ')
            except:
                related_words = []
        if len(related_words) > 0:
            # Assign first non-numeric string to keyword for filter
            keyword = ''
            index = 0
            while keyword == '' and index < len(related_words):
                print(related_words[index], keyword)
                try:
                    float(related_words[index])
                    index += 1
                except ValueError:
                    keyword = related_words[index]
                    index += 1

            self.drug_list = RegisteredDrug.objects.filter(
                Q(ingredients__name__icontains=keyword) |
                Q(name__icontains=keyword)
            ).order_by('name')[:100]
        else:
            self.drug_list = None
        data['drug_obj'] = self.drug_obj
        data['deliveryitem_obj_list'] = self.deliveryitem_obj_list
        data['cmsitem_obj'] = self.object
        data['drug_list'] = self.drug_list
        data['related_keyword'] = keyword 
        return data

class InventoryItemModalDetail(BSModalReadView, LoginRequiredMixin):
    model = InventoryItem
    template_name = 'cmsinv/inventory_item_modal_detail.html'
    cmsitem_obj = None
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
        data['cmsitem_obj'] = self.object
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
    drug_obj = None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
        except:
            self.drug_obj = None
        data['drug_obj'] = self.drug_obj
        data['item_obj'] = self.object
        data['next_clinic_no'] = InventoryItem.generateNextClinicDrugNo()
        return data

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        form.instance.date_created = timezone.now()
        form.instance.last_updated = timezone.now()
        form.instance.version = self.object.version + 1
        response = super().form_valid(form)

        # Update corresponding inventory.Item
        if form.instance.registration_no:
            reg_no = form.instance.registration_no.upper()
        else:
            reg_no = None
        item_data = {
            'name': form.instance.product_name,
            'cmsid': self.object.id,
            'reg_no': reg_no,
            'item_type': ItemType.objects.get(name="Drug"),  # CMS InventoryItems are by default "Drug"
            'is_active': not form.instance.discontinue,
        }
        item, created = Item.objects.update_or_create(cmsid=self.object.id, defaults=item_data)
        if created:
            print(f'Item #{item.id} created: {item.name}')
        else:
            print(f"Item #{item.id} updated: {item.name}")
        return response

    def get_success_url(self):
        return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))

# class InventoryItemDelete(DeleteView, LoginRequiredMixin):
#     """Delete drug delivery record"""
#     model = InventoryItem
#     success_url = reverse_lazy('cmsinv:InventoryItemList')

class NewInventoryItem(CreateView, LoginRequiredMixin):
    """Add new CMS inventory item"""
    model = InventoryItem
    template_name = 'cmsinv/new_inventory_item.html'
    form_class = NewInventoryItemForm
    context_object_name = 'new_inventory_item'
    regdrug_obj = None
    drug_reg_no = ''
    vendor_obj = None

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('reg_no'):
            self.drug_reg_no = request.GET.get('reg_no')
            try:
                self.regdrug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
            except:
                self.regdrug_obj = None
        else:
            self.drug_reg_no = ''
        if request.GET.get('vendor'):
            try:
                self.vendor_obj = Vendor.objects.get(pk=request.GET.get('vendor'))
            except:
                self.vendor_obj = None
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.regdrug_obj:
            data['regdrug_obj'] = self.regdrug_obj
        else:
            data['product_name'] = ''
        return data

    def get_form_kwargs(self):
        kwargs = super(NewInventoryItem, self).get_form_kwargs()
        kwargs.update({
            'regdrug_obj': self.regdrug_obj,
            'vendor_obj': self.vendor_obj,
            })
        return kwargs

    def form_valid(self, form):
        print(f'Form valid, {self.regdrug_obj} / {self.vendor_obj}')
        user = self.request.user.username
        uri = reverse('cmsinv:NewInventoryItem')
        form.instance.updated_by = user
        form.instance.version = 0
        form.instance.date_created = timezone.now()
        form.instance.last_updated = timezone.now()
        session_id = self.request.session.session_key

        if self.regdrug_obj:  # Assign cert_holder if RegisteredDrug
            cert_holder_data = {
                'name': self.regdrug_obj.company.name,
                'address': self.regdrug_obj.company.address,
                'supp_type': 'Certificate Holder',
                'date_created': timezone.now(),
                'last_updated': timezone.now(),
                'updated_by': user,
            }
            cert_holder_obj, created = Supplier.objects.get_or_create(
                name=self.regdrug_obj.company.name.upper(),
                defaults=cert_holder_data,
                )
            if created: # Update AuditLog
                print(f"Cert Holder created: {cert_holder_obj}")

                audit_str_dict = {**cert_holder_data,
                    'dateCreated': datetime.strftime(cert_holder_obj.date_created, "%a %b %d %H:%M:%S %Z %Y"),
                    'lastUpdated': datetime.strftime(cert_holder_obj.last_updated, "%a %b %d %H:%M:%S %Z %Y"),
                    'type': 'Supplier',
                }
                sorted_dict = dict(sorted(audit_str_dict.items()))
                audit_str = "||".join([
                    ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
                ])
                
                newAuditLogEntry = AuditLog(
                    actor = user,
                    class_name = 'SupplierManufacturer',
                    event_name = 'INSERT',
                    old_value = None,
                    new_value = audit_str,
                    persisted_object_version = 'null',
                    persisted_object_id = cert_holder_obj.id,
                    session_id = session_id,
                    uri = uri,
                )
                newAuditLogEntry.save()
                if newAuditLogEntry.id:
                    print(f"New audit log entry added: {audit_str}")
                else:
                    print("Error writing audit log entry")
            form.instance.certificate_holder = cert_holder_obj
            form.instance.registration_no = self.regdrug_obj.reg_no
            form.instance.inventory_item_type = InventoryItemType.objects.get(id=1)

        elif self.vendor_obj:  # Assign vendor if given
            new_supplier_data = {
                'name': self.vendor_obj.name,
                'address': self.vendor_obj.address,
                'supp_type': 'Supplier',
                'date_created': timezone.now(),
                'last_updated': timezone.now(),
                'updated_by': user,
            }
            supplier_obj, created = Supplier.objects.get_or_create(
                name=self.vendor_obj.name.upper(),
                defaults=vendor_data,
            )
            if created: # Update AuditLog
                print(f"New supplier added: ({supplier_obj.name})")

                audit_str_dict = {**new_supplier_data,
                    'dateCreated': datetime.strftime(supplier_obj.date_created, "%a %b %d %H:%M:%S %Z %Y"),
                    'lastUpdated': datetime.strftime(supplier_obj.last_updated, "%a %b %d %H:%M:%S %Z %Y"),
                    'type': 'Supplier',
                }
                sorted_dict = dict(sorted(audit_str_dict.items()))
                audit_str = "||".join([
                    ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
                ])
                
                newAuditLogEntry = AuditLog(
                    actor = user,
                    class_name = 'SupplierManufacturer',
                    event_name = 'INSERT',
                    old_value = None,
                    new_value = audit_str,
                    persisted_object_version = 'null',
                    persisted_object_id = supplier_obj.id,
                    session_id = session_id,
                    uri = uri,
                )
                newAuditLogEntry.save()
                if newAuditLogEntry.id:
                    print(f"New audit log entry added: {audit_str}")
                else:
                    print("Error writing audit log entry")
            form.instance.certificate_holder = supplier_obj
        
        # Submit form 
        response = super().form_valid(form)

        # Successful save => Update AuditLog for InventoryItem
        audit_str_dict = model_to_dict(self.object)
        sorted_dict = dict(sorted(audit_str_dict.items()))
        audit_str = "||".join([
            ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
        ])
        newAuditLogEntry = AuditLog(
            actor = user,
            class_name = 'InventoryItem',
            event_name = 'INSERT',
            old_value = None,
            new_value = audit_str,
            persisted_object_version = 'null',
            persisted_object_id = self.object.id,
            session_id = session_id,
            uri = uri,
        )
        newAuditLogEntry.save()
        if newAuditLogEntry.id:
            print(f"New audit log entry added: {audit_str}")
        else:
            print("Error writing audit log entry")

        # Create new corresponding inventory.Item if not existing
        if self.object.registration_no:
            reg_no = form.instance.registration_no.upper()
        else:
            reg_no = None
        item_data = {
            'name': self.object.product_name,
            'cmsid': self.object.id,
            'reg_no': reg_no,
            'item_type': ItemType.objects.get(value=1),
            'is_active': True,
            'updated_by': self.request.user.username,
            'last_updated': timezone.now(),
        }
        if reg_no:
            item_obj, created = Item.objects.get_or_create(
                reg_no=reg_no, defaults=item_data,
            )
        else:
           item_obj, created = Item.objects.get_or_create(
            id=cmsid, defaults=item_data,
        ) 
        if created:
            print(f"Item created: {item_obj}")

            # Update RegDrug object if it is a registered drug
            if self.regdrug_obj:
                self.regdrug_obj.itemid = item_obj.id
                self.regdrug_obj.save()
                print(f"RegDrug {self.regdrug_obj.reg_no} updated with itemid {self.regdrug_obj.itemid}")
        else:
            print(f"Item #{ item_obj.id } updated: {item_obj}")
        return response

    def get_success_url(self):
        return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))

# class MatchInventoryItemList(ListView, LoginRequiredMixin):
#     """
#     CMS Inventory Item List Matching Non-CMS Delivery Record
#     """
#     model = InventoryItem
#     template_name = "cmsinv/match_inventory_item_list.html"
#     context_object_name = 'match_item_list_obj'
#     drug_reg_no = ''
#     keyword = ''
#     ingredients = ''
#     drug_obj = None
#     delivery_obj_list = None
#     cmsitem_obj = None

#     def dispatch(self, request, *args, **kwargs):
#         if 'reg_no' in kwargs:
#             self.drug_reg_no = kwargs['reg_no']
#             try:
#                 self.cmsitem_obj = InventoryItem.objects.get(registration_no=self.drug_reg_no)
#             except InventoryItem.DoesNotExist:
#                 self.cmsitem_obj = None
#             try:
#                 self.drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
#             except RegisteredDrug.DoesNotExist:
#                 self.drug_obj = None 
#             try:
#                 self.delivery_obj_list = DeliveryItem.objects.filter(item__reg_no=self.drug_reg_no)[:5]
#             except DeliveryItem.DoesNotExist:
#                 self.delivery_obj_list = None

#         else:
#             print("Error: missing reg_no")
#         return super().dispatch(request, *args, **kwargs)
    
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['drug_obj'] =  self.drug_obj
#         data['cmsitem_obj'] = self.cmsitem_obj
#         data['delivery_obj_list'] = self.delivery_obj_list
#         return data

#     def get_queryset(self):
#         if self.drug_obj:
#             self.keyword = self.drug_obj.name
#             self.ingredients = self.drug_obj.ingredients_list
#         else:
#             print('Error no existing reg no.')
#         if self.keyword == None:
#             self.keyword = ''
#         if self.ingredients == None:
#             self.ingredients = ''
#         object_list = InventoryItem.objects.filter(
#             Q(product_name__icontains=self.keyword) |
#             Q(generic_name__icontains=self.keyword) |
#             Q(alias__icontains=self.keyword) |
#             Q(ingredient__icontains=self.ingredients)
#         ).order_by('discontinue').exclude(registration_no=self.drug_reg_no)[:100]
#         return object_list

# class InventoryItemMatchUpdate(UpdateView, LoginRequiredMixin):
#     """
#     CMS Inventory Item List Matching Non-CMS Delivery Record
#     """
#     model = InventoryItem
#     template_name = 'cmsinv/inventory_item_match_update.html'
#     form_class = InventoryItemMatchUpdateForm
#     item_obj = None
#     drug_obj = None
#     possible_drug_list = None
#     delivery_obj = None
#     delivery_obj_list = None
    
#     def get_success_url(self):
#         return reverse('cmsinv:InventoryItemDetail', args=(self.object.pk,))
        
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         try:
#             self.drug_obj = RegisteredDrug.objects.get(reg_no=self.object.registration_no)
#         except RegisteredDrug.DoesNotExist:
#             print(f"No registration no. for {self.object.product_name}")
            
#         try:
#             self.delivery_obj_list = DeliveryItem.objects.filter(item__reg_no=self.object.registration_no).order_by('-delivery_order__received_date')[:5]
#         except DeliveryItem.DoesNotExist:
#             self.delivery_obj_list = None
#             print(f"No delivery record for {self.object.product_name}")
#         if self.delivery_obj_list:
#             self.delivery_obj = self.delivery_obj_list[0]
#         data['drug_obj'] = self.drug_obj
#         data['delivery_obj'] = self.delivery_obj
#         data['delivery_obj_list'] = self.delivery_obj_list
#         data['item_obj'] = self.object
#         return data

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

class InventoryMovementLogList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Displays InventoryMovementLog
    """
    DELIVERY = '1'
    DISPENSARY = '2'
    RECONCILIATION = '3'
    STOCK_INIT = '4'
    MOVEMENT_TYPE_CHOICES = [
        (DELIVERY, 'Delivery'),
        (DISPENSARY, 'Dispensary'),
        (RECONCILIATION, 'Reconciliation'),
        (STOCK_INIT, 'Stock Initialization'),
    ]
    permission_required = ('cmsinv.view_inventorymovementlog',)
    template_name = 'cmsinv/inventory_movement_log.html'
    model = InventoryMovementLog
    context_object_name = 'cmsinv_move_log'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        self.disp_type = self.request.GET.get('t') or ''
        if self.disp_type:
            move_type = dict(self.MOVEMENT_TYPE_CHOICES).get(self.disp_type)
            print(move_type)
            object_list = InventoryMovementLog.objects.filter(movement_type=move_type).order_by('-last_updated')
        else:
            object_list = InventoryMovementLog.objects.all().order_by('-last_updated')
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = object_list.filter(
                Q(move_item__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = object_list.order_by('-last_updated')
            self.last_query_count = object_list.count
        if self.begin:
            object_list = object_list.filter(received_date__gte=self.begin)
        if self.end:
            object_list = object_list.filter(received_date__lte=self.end)
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['disp_type'] = self.disp_type
        data['begin'] = self.begin
        data['end'] = self.end
        return data


# class NewDeliveryFromDeliveryOrderModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
#     """
#     Creates new CMS Delivery from DeliveryOrder
#     """
#     permission_required = ('cmsinv.view_inventorymovementlog',)
#     template_name = 'cmsinv/new_delivery_from_deliveryorder_modal.html'
#     model = Delivery
#     form_class = NewDeliveryFromDeliveryOrderModalForm
    
def underscore_to_camel(word):
    return word.split('_')[0] + ''.join(x.capitalize() or '_' for x in word.split('_')[1:])

@login_required
def NewDeliveryFromDeliveryOrderModalView(request, *args, **kwargs):
    if kwargs['delivery_id']:
        delivery_obj = get_object_or_404(DeliveryOrder, pk=kwargs['delivery_id'])
    else:
        print("Error: no delivery_id")
    uri = request.GET.get('next', reverse('inventory:DeliveryOrderDetail', args=(delivery_obj.id,)))
    session_id = request.session.session_key
    # Get cmsuser id
    cmsuser_obj = CmsUser.objects.get(username='cmsman')
    itemupdate_list = []
    for listitem in delivery_obj.delivery_items.all():
        if listitem.item.cmsid:
            cmsitem_obj = InventoryItem.objects.get(id=listitem.item.cmsid)
            summary = {
                'name': listitem.item.name,
                'cmsid': listitem.item.cmsid,
                'discontinue': cmsitem_obj.discontinue,
                'existing_qty': cmsitem_obj.stock_qty,
                'old_standard_cost': cmsitem_obj.standard_cost,
                'old_avg_cost': cmsitem_obj.avg_cost,
                'items_quantity': listitem.items_quantity,
                'new_standard_cost': listitem.standard_cost,
                'new_avg_cost': listitem.average_cost,
            }
            itemupdate_list.append(summary)

    context = {
        'delivery_obj': delivery_obj,
        'itemupdate_list': itemupdate_list,
        'itemupdate_count': len(itemupdate_list),
    }
    # If POST request confirm sync, add data to CMS
    if request.method == "POST":
        if len(itemupdate_list) == 0:
            # Set delivery order status to cms_synced
            delivery_obj.cms_synced = True
            delivery_obj.save()
        else:
            # Get or create CMS supplier based on vendor name
            new_supplier_data = {
                'address': delivery_obj.vendor.address,
                'name': delivery_obj.vendor.name,
                'supp_type': 'Supplier',
                'updated_by': cmsuser_obj.username,
            }
            supplier_obj, supplier_created = Supplier.objects.get_or_create(
                name__iexact=delivery_obj.vendor.name, 
                defaults=new_supplier_data
            )
            if supplier_created:  # Update AuditLog
                print(f"New supplier added: ({supplier_obj.name})")

                audit_str_dict = {**new_supplier_data,
                    'dateCreated': datetime.strftime(supplier_obj.date_created, "%a %b %d %H:%M:%S %Z %Y"),
                    'lastUpdated': datetime.strftime(supplier_obj.last_updated, "%a %b %d %H:%M:%S %Z %Y"),
                    'type': 'Supplier',
                }
                sorted_dict = dict(sorted(audit_str_dict.items()))
                audit_str = "||".join([
                    ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
                ])
                
                newAuditLogEntry = AuditLog(
                    actor = cmsuser_obj.username,
                    class_name = 'SupplierManufacturer',
                    event_name = 'INSERT',
                    old_value = None,
                    new_value = audit_str,
                    persisted_object_version = 'null',
                    persisted_object_id = supplier_obj.id,
                    session_id = session_id,
                    uri = uri,
                )
                newAuditLogEntry.save()
                if newAuditLogEntry.id:
                    print(f"New audit log entry added: {audit_str}")
                else:
                    print("Error writing audit log entry")
            
            # Get or create CMS delivery record
            new_cmsdelivery_data = {
                'cash_amount': 0,  # payment tracking not via CMS
                'total_cost': delivery_obj.items_total,
                'create_date': delivery_obj.invoice_date,
                'received_by': cmsuser_obj,
                'supplierdn': delivery_obj.invoice_no,
                'delivery_note_no': delivery_obj.id,
                'updated_by': cmsuser_obj.username,
                'supplier': supplier_obj, 
            }
            cmsdelivery_obj, cmsdelivery_created = Delivery.objects.get_or_create(
                delivery_note_no=delivery_obj.id, 
                defaults=new_cmsdelivery_data
            )
            if cmsdelivery_created:  # Update DeliveryOrder record and AuditLog
                print(f"New delivery added: id #{cmsdelivery_obj.id}")
                delivery_obj.cms_delivery_id = cmsdelivery_obj.id
                delivery_obj.cms_synced = True
                delivery_obj.save()

                audit_str_dict = {**new_cmsdelivery_data,
                    'dateCreated': datetime.strftime(cmsdelivery_obj.date_created, "%a %b %d %H:%M:%S %Z %Y"),
                    'lastUpdated': datetime.strftime(cmsdelivery_obj.last_updated, "%a %b %d %H:%M:%S %Z %Y"),
                    'type': 'Delivery',
                }
                sorted_dict = dict(sorted(audit_str_dict.items()))
                audit_str = "||".join([
                    ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
                ])
                
                newAuditLogEntry = AuditLog(
                    actor = cmsuser_obj.username,
                    class_name = 'Delivery',
                    event_name = 'INSERT',
                    old_value = None,
                    new_value = audit_str,
                    persisted_object_version = 'null',
                    persisted_object_id = cmsdelivery_obj.id,
                    session_id = session_id,
                    uri = uri,
                )
                newAuditLogEntry.save()
                if newAuditLogEntry.id:
                    print(f"New audit log entry added: {audit_str}")
                else:
                    print("Error writing audit log entry")
            else:
                print(f"Delivery order already synced to CMS")

            # Loop through DeliveryOrder item list and add to CMS received_item
            item_idx = 0
            for listitem in delivery_obj.delivery_items.all():
                # Get CMS Inventory Item object
                if listitem.item.cmsid:
                    cmsitem_obj = InventoryItem.objects.get(id=listitem.item.cmsid)
                    if listitem.batch_num:
                        lot_no = listitem.batch_num
                    else:
                        lot_no = ""
                    new_cmsreceived_item = {
                        'arrive_date': delivery_obj.invoice_date,
                        'cost': listitem.total_price,
                        'dangerous_sign': cmsitem_obj.dangerous_sign,
                        'delivery': cmsdelivery_obj,
                        'drug_item': cmsitem_obj,
                        'expire_date': listitem.expiry_date,
                        'lot_no': lot_no,
                        'quantity': listitem.items_quantity,
                        'unit': listitem.items_unit,
                        'received_items_idx': item_idx,
                        'remarks': listitem.terms,
                    }
                    cmsreceived_obj, cmsreceived_created = ReceivedItem.objects.update_or_create(
                        drug_item=cmsitem_obj,
                        quantity=listitem.items_quantity,
                        cost=listitem.total_price,
                        lot_no=lot_no,
                        defaults=new_cmsreceived_item
                    )
                    if cmsreceived_created:  # Update InventoryItem, InventoryMovementLog, AuditLog
                        print(f"New received item added: {cmsreceived_obj}")
                        
                        # Update InventoryItem quantity/costs
                        last_updated = timezone.now()
                        old_stock_qty = cmsitem_obj.stock_qty
                        old_standard_cost = cmsitem_obj.standard_cost
                        old_avg_cost = cmsitem_obj.avg_cost
                        old_discontinue = 'true' if cmsitem_obj.discontinue else 'false'
                        old_is_clinic_drug_list = 'false' if cmsitem_obj.is_clinic_drug_list else 'true'
                        old_clinic_drug_no = cmsitem_obj.clinic_drug_no
                        cmsitem_obj.stock_qty += float(listitem.items_quantity)
                        if listitem.standard_cost != 0:
                            cmsitem_obj.standard_cost = listitem.standard_cost
                        if listitem.average_cost != 0:
                            cmsitem_obj.avg_cost = listitem.average_cost
                        cmsitem_obj.discontinue = False
                        cmsitem_obj.is_clinic_drug_list = True
                        cmsitem_obj.clinic_drug_no = InventoryItem.generateNextClinicDrugNo()
                        cmsitem_obj.updated_by = cmsuser_obj.username
                        cmsitem_obj.last_updated = last_updated
                        cmsitem_obj.save()
                        if cmsitem_obj.last_updated == last_updated:
                            # Successful save
                            print(f"Updated inventory item: {cmsitem_obj.product_name}")
                        
                            # Update AuditLog:InventoryItem - stock_qty
                            newAuditLogEntry = AuditLog(
                                actor = cmsuser_obj.username,
                                class_name = 'InventoryItem',
                                event_name = 'UPDATE',
                                old_value = str(old_stock_qty),
                                new_value = str(cmsitem_obj.stock_qty),
                                persisted_object_version = 'null',
                                persisted_object_id = cmsitem_obj.id,
                                property_name = "stockQty",
                                session_id = session_id,
                                uri = uri,
                            )
                            newAuditLogEntry.save()
                            if newAuditLogEntry.id:
                                print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                            else:
                                print("Error writing audit log entry")

                            # Update AuditLog:InventoryItem - standard_cost if not 0
                            if listitem.standard_cost !=0:
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryItem',
                                    event_name = 'UPDATE',
                                    old_value = str(old_standard_cost),
                                    new_value = str(cmsitem_obj.standard_cost),
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsitem_obj.id,
                                    property_name = "standardCost",
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                                else:
                                    print("Error writing audit log entry")

                            # Update AuditLog:InventoryItem - avg_cost
                            if listitem.average_cost != 0:
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryItem',
                                    event_name = 'UPDATE',
                                    old_value = str(old_avg_cost),
                                    new_value = str(cmsitem_obj.avg_cost),
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsitem_obj.id,
                                    property_name = "avgCost",
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                                else:
                                    print("Error writing audit log entry")

                            # Update AuditLog:InventoryItem - discontinue - if changed.
                            if old_discontinue:
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryItem',
                                    event_name = 'UPDATE',
                                    old_value = 'true',
                                    new_value = 'false',
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsitem_obj.id,
                                    property_name = "discontinue",
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                                else:
                                    print("Error writing audit log entry")
                            # Update AuditLog:InventoryItem - is_clinic_drug_list
                            if not old_is_clinic_drug_list:
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryItem',
                                    event_name = 'UPDATE',
                                    old_value = 'false',
                                    new_value = 'true',
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsitem_obj.id,
                                    property_name = "is_clinic_drug_list",
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                                else:
                                    print("Error writing audit log entry")
                            # Update AuditLog:InventoryItem - clinic_drug_no - if changed
                            if old_clinic_drug_no != cmsitem_obj.clinic_drug_no:
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryItem',
                                    event_name = 'UPDATE',
                                    old_value = old_clinic_drug_no,
                                    new_value = cmsitem_obj.clinic_drug_no,
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsitem_obj.id,
                                    property_name = "clinic_drug_no",
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added UPDATE:{newAuditLogEntry.property_name} {newAuditLogEntry.old_value}=>{newAuditLogEntry.new_value}")
                                else:
                                    print("Error writing audit log entry")

                            # Add new InventoryMovementLog record
                            new_invmovelog_data = {
                                'lot_no': listitem.batch_num,
                                'move_item': listitem.item.name,
                                'quantity': listitem.items_quantity,
                                'movement_type': 'Delivery',
                                'updated_by': cmsuser_obj.username,
                                'reference_no': cmsdelivery_obj.id,
                            }
                            newInventoryMovementLogEntry = InventoryMovementLog(
                                **new_invmovelog_data,
                            )
                            newInventoryMovementLogEntry.save()
                            if newInventoryMovementLogEntry.id:
                                # Successful save
                                print(f"New InventoryMovementLog added: {newInventoryMovementLogEntry}")

                                # Update AuditLog for InventoryMovementLog
                                ## Rename movement_type to type
                                new_invmovelog_data['type'] = new_invmovelog_data.pop('movement_type')
                                audit_str_dict = {**new_invmovelog_data,
                                    'dateCreated': datetime.strftime(newInventoryMovementLogEntry.date_created, "%a %b %d %H:%M:%S %Z %Y"),
                                    'lastUpdated': datetime.strftime(newInventoryMovementLogEntry.last_updated, "%a %b %d %H:%M:%S %Z %Y"),
                                }
                                sorted_dict = dict(sorted(audit_str_dict.items()))
                                audit_str = "||".join([
                                    ":=".join((underscore_to_camel(key), str(value))) for (key, value) in sorted_dict.items()
                                ])
                                
                                newAuditLogEntry = AuditLog(
                                    actor = cmsuser_obj.username,
                                    class_name = 'InventoryMovementLog',
                                    event_name = 'INSERT',
                                    old_value = None,
                                    new_value = audit_str,
                                    persisted_object_version = 'null',
                                    persisted_object_id = cmsdelivery_obj.id,
                                    session_id = session_id,
                                    uri = uri,
                                )
                                newAuditLogEntry.save()
                                if newAuditLogEntry.id:
                                    print(f"New audit log entry added: {audit_str}")
                                else:
                                    print("Error writing audit log entry")
                            else:
                                print("Error updating inventory log")
                        else:
                            print("CMS InventoryItem not updated")
                    else:
                        print(f"Already existing: {cmsreceived_obj}")
                    item_idx += 1
                else:
                    print(f"Skipping item {listitem.item.name} - not a CMS item")
        return redirect(uri)
    
    return render(request, "cmsinv/new_delivery_from_deliveryorder_modal.html", context)

