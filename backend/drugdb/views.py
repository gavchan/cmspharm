from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from bootstrap_modal_forms.generic import BSModalCreateView

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from ledger.models import (
    Expense,
)
from .models import (
    RegisteredDrug,
    Company,
    DrugDelivery,
)
from .forms import (
    NewDrugDeliveryForm, DrugDeliveryUpdateForm,
    BillDrugDeliveryAddDrugModalForm,
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
  
class DrugDeliveryList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists drug deliveries
    """
    permission_required = ('drugdb.view_drugdelivery')
    template_name = 'drugdb/drug_delivery_list.html'
    model = DrugDelivery
    context_object_name = 'drug_delivery_list'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = DrugDelivery.objects.filter(
                Q(product_name__icontains=query) |
                Q(reg_no__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = DrugDelivery.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data

class DrugDeliveryDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Display details of drug delivery"""
    permission_required = ('drugdb.view_drugdelivery')
    model = DrugDelivery
    template_name = 'drugdb/drug_delivery_detail.html'
    context_object_name = 'delivery_obj'

class DrugDeliveryUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update details of drug delivery"""
    permission_required = ('drugdb.change_drugdelivery', )
    model = DrugDelivery
    form_class = DrugDeliveryUpdateForm
    template_name = 'drugdb/drug_delivery_update_form.html'


    def get_success_url(self):
        return reverse('drugdb:DrugDeliveryDetail', args=(self.object.pk,))

class DrugDeliveryDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Delete drug delivery record"""
    permission_required = ('drugdb.view_drugdelivery', 'drugdb.delete_drugdelivery')
    model = DrugDelivery
    success_url = reverse_lazy('drugdb:DrugDeliveryList')

class NewDrugDelivery(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new drug delivery"""
    permission_required = ('drugdb.view_drugdelivery', 'drugdb.add_drugdelivery')
    model = DrugDelivery
    template_name = 'drugdb/new_drug_delivery.html'
    form_class = NewDrugDeliveryForm
    context_object_name = 'new_drug_delivery'
    drug_reg_no = ''
    cmsinv_item_obj = None

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
            drug_obj = RegisteredDrug.objects.get(reg_no=self.drug_reg_no)
            data['product_name'] = drug_obj.name
            data['vendor'] = drug_obj.company
            try:
                self.cmsinv_item_obj = InventoryItem.objects.get(registration_no=self.drug_reg_no)
            except:
                print("Error: CMS inventory does not have item that matches reg. no. {self.drug_reg_no}")

        else:
            print("Error: missing reg_no")
            data['product_name'] = ''
        data['cmsinv_item_obj'] = self.cmsinv_item_obj
        return data

# class BillDrugDeliveryList(ListView, LoginRequiredMixin):
#     """Add new drug delivery to bill"""
#     model = DrugDelivery
#     template_name = 'drugdb/bill_drugdelivery_view.html'
#     context_object_name = 'bill_delivery_item_list'
#     bill_obj = None

#     def dispatch(self, request, *args, **kwargs):
#         if 'bill_id' in kwargs:
#             self.bill_obj = Expense.objects.get(id=kwargs['bill_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def get_queryset(self):
#         return DrugDelivery.objects.filter(bill=self.bill_obj)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         if self.bill_obj:
#             data['bill_obj'] = self.bill_obj
#         return data

@login_required
@permission_required('drugdb.view_drugdelivery', 'ledger.view_bill')
def BillDrugDeliveryView(request, *args, **kwargs):
    """View Bill with DrugDelivery items"""
    MAX_QUERY_COUNT = 20

    # Parse bill_id from request and get related Expense
    bill_obj = None
    if 'bill_id' in kwargs:
        bill_obj = Expense.objects.get(id=kwargs['bill_id'])
        print(bill_obj.id)
    ctx = {
        'bill_obj': bill_obj
    }

    # Get related DrugDelivery objects associated with bill_id
    bill_items_list = DrugDelivery.objects.filter(bill=bill_obj)
    ctx['bill_items_list'] = bill_items_list

    # Get query from request and search RegisteredDrug    
    query = request.GET.get('q')
    print(query)
    if query:
        last_query = query
        object_list = RegisteredDrug.objects.filter(
            Q(name__icontains=query) |
            Q(reg_no__icontains=query) |
            Q(ingredients__icontains=query)
        )[:MAX_QUERY_COUNT]
        last_query_count = object_list.count
    else:
        last_query = ''
        object_list = RegisteredDrug.objects.all()[:MAX_QUERY_COUNT]
        last_query_count = object_list.count

    if request.is_ajax():
        html = render_to_string(
            template_name='drugdb/_drug_search_results_partial.html',
            context={
                'drug_list': object_list,
                'bill_id': bill_obj.id
                }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "drugdb/bill_drugdelivery_view.html", context=ctx)

# class BillDrugDeliveryChooseDrugModal(ListView, LoginRequiredMixin):
#     """Modal to choose drug to add to bill"""
#     template_name = 'drugdb/bill_drugdelivery_choose_drug_modal.html'
#     model = RegisteredDrug
#     context_object_name = 'drug_list'
#     bill_obj = None

#     def dispatch(self, request, *args, **kwargs):
#         if 'bill_id' in kwargs:
#             self.bill_obj = Expense.objects.get(id=kwargs['bill_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         if query:
#             self.last_query = query
#             object_list = RegisteredDrug.objects.filter(
#                 Q(name__icontains=query) |
#                 Q(reg_no__icontains=query) |
#                 Q(ingredients__icontains=query)
#             )[:30]
#             self.last_query_count = object_list.count
#         else:
#             self.last_query = ''
#             object_list = RegisteredDrug.objects.all()[:30]
#             self.last_query_count = object_list.count
#         return object_list

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['last_query'] = self.last_query
#         data['last_query_count'] = self.last_query_count
#         return data

class BillDrugDeliveryAddDrugModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new drug delivery to bill"""
    permission_required = ('drugdb.add_drugdelivery', 'ledger.add_bill')
    template_name = 'drugdb/bill_drugdelivery_add_modal.html'
    form_class = BillDrugDeliveryAddDrugModalForm
    bill_obj = None
    drug_obj = None
    success_message = 'Success: Drug added'

    def dispatch(self, request, *args, **kwargs):
        if 'bill_id' in kwargs:
            self.bill_obj = Expense.objects.get(id=kwargs['bill_id'])
        else:
            print('Error: no bill_id')
        if 'reg_no' in kwargs:
            self.drug_obj = RegisteredDrug.objects.get(reg_no=kwargs['reg_no'])
        else:
            print('Error: no drug reg_no')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.bill_obj:
            data['bill_obj'] = self.bill_obj
        return data

    def get_success_url(self):
        return reverse('drugdb:BillDrugDeliveryView', args=(self.bill_obj.pk,))

    def get_form_kwargs(self):
        kwargs = super(BillDrugDeliveryAddDrugModal, self).get_form_kwargs()
        kwargs.update({
            'bill_obj': self.bill_obj,
            'drug_obj': self.drug_obj,
            })
        return kwargs