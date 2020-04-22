from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from .models import (
    RegisteredDrug,
    Company,
    DrugDelivery,
)
from .forms import NewDrugDeliveryForm, DrugDeliveryUpdateForm

class RegisteredDrugList(ListView, LoginRequiredMixin):
    """List of registered drugs"""
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
                Q(registration_no__icontains=query) |
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

class RegisteredDrugDetail(DetailView, LoginRequiredMixin):
    """Display details for registered drug"""
    model = RegisteredDrug
    template_name = 'drugdb/drug_detail.html'
    context_object_name = 'drug_detail'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

class CompanyList(ListView, LoginRequiredMixin):
    """List of Companies"""
    template_name = 'drugdb/company_list.html'
    model = Company
    context_object_name = 'company_list'
    paginate_by = 20

    def get_queryset(self):
        return Company.objects.all()
  
class DrugDeliveryList(ListView, LoginRequiredMixin):
    """
    Lists drug deliveries
    """
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
                Q(registration_no__icontains=query)
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

class DrugDeliveryDetail(DetailView, LoginRequiredMixin):
    """Display details of drug delivery"""
    model = DrugDelivery
    template_name = 'drugdb/drug_delivery_detail.html'
    context_object_name = 'delivery_obj'

class DrugDeliveryUpdate(UpdateView, LoginRequiredMixin):
    """Update details of drug delivery"""
    model = DrugDelivery
    form_class = DrugDeliveryUpdateForm
    template_name = 'drugdb/drug_delivery_update_form.html'

    def get_success_url(self):
        return reverse('drugdb:DrugDeliveryDetail', args=(self.object.pk,))
    # context_object_name = 'delivery_obj'

class DrugDeliveryDelete(DeleteView, LoginRequiredMixin):
    """Delete drug delivery record"""
    model = DrugDelivery
    success_url = reverse_lazy('drugdb:DrugDeliveryList')

class NewDrugDelivery(CreateView, LoginRequiredMixin):
    """Add new drug delivery"""
    template_name = 'drugdb/new_drug_delivery.html'
    form_class = NewDrugDeliveryForm
    context_object_name = 'new_drug_delivery'
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
            drug_obj = RegisteredDrug.objects.get(registration_no=self.drug_reg_no)
            data['product_name'] = drug_obj.name
        else:
            print("Error: missing reg_no")
            data['product_name'] = ''
        return data