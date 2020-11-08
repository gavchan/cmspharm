from datetime import date
import csv
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from .models import (
    ExpenseCategory,
    Expense
)

from .forms import (
    NewExpenseCategoryForm, ExpenseCategoryUpdateForm,
    NewExpenseForm, ExpenseUpdateForm,
    ExpenseUpdateModalForm,
    # NewExpenseByVendorModalForm,
    NewExpenseModalForm,
)
from inventory.models import (
    Vendor,
)

# Expense Category Views
# ======================

class ExpenseCategoryList(ListView, LoginRequiredMixin):
    model = ExpenseCategory
    template_name = "ledger/expense_category_list.html"
    context_object_name = 'expense_category_list_obj'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = ExpenseCategory.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = ExpenseCategory.objects.all()
            self.last_query_count = object_list.count
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data

class ExpenseCategoryUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('ledger.change_expensecategory',)
    model = ExpenseCategory
    form_class = ExpenseCategoryUpdateForm
    template_name = "ledger/expense_category_update.html"
    success_url = reverse_lazy('ledger:ExpenseCategoryList')

class NewExpenseCategory(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new vendor"""
    permission_required = ('ledger.add_expensecategory')
    model = ExpenseCategory
    template_name = 'ledger/new_expense_category.html'
    form_class = NewExpenseCategoryForm
    success_url = reverse_lazy('ledger:ExpenseCategoryList')

# Expense Views
# =============

class ExpenseList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """Lists Expenses"""
    permission_required = ('ledger.view_expense')
    model = Expense
    template_name = "ledger/expense_list.html"
    context_object_name = 'expense_list_obj'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    today =  date.today().strftime('%Y-%m-%d')
    begin = ''
    end = ''

    def get_queryset(self):
        query = self.request.GET.get('q')
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        print(f"Date from: {self.begin} to: {self.end}")
        if query:
            self.last_query = query
            object_list = Expense.objects.filter(
                Q(description__icontains=query) |
                Q(payee__icontains=query)
            ).order_by('-expected_date')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = Expense.objects.all().order_by('-expected_date')
            self.last_query_count = object_list.count
        if self.begin and self.end:
            # Filter date range if both parameters given
            object_list = object_list.filter(expected_date__range=[self.begin, self.end])
        elif self.begin and not self.end:
            # Filter for items later than begin date
            object_list = object_list.filter(expected_date__gte=self.begin)
        elif self.end and not self.begin:
            object_list = object_list.filter(expected_date__lte=self.end)

        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        data['begin'] = self.begin
        data['end'] = self.end
        return data

class ExpenseUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Expense"""
    permission_required = ('ledger.change_expense',)
    model = Expense
    form_class = ExpenseUpdateForm
    template_name = "ledger/expense_update.html"
    success_message = 'Success: Expense was updated'
    success_url = reverse_lazy('ledger:ExpenseList')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['expense_obj'] = self.object
        return data

class ExpenseDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Expense modal"""
    permission_required = ('ledger.delete_expense',)
    model = Expense
    template_name = 'ledger/expense_confirm_delete_modal.html'
    success_message = 'Success: Expense was deleted.'
    success_url = reverse_lazy('ledger:ExpenseList')

# class NewExpenseByVendorModal(BSModalCreateView, LoginRequiredMixin):
#     template_name = 'ledger/new_expense_by_vendor_modal.html'
#     form_class = NewExpenseByVendorModalForm
#     success_url = reverse_lazy('ledger:ExpenseList')
#     vendor_obj = None
    
#     def dispatch(self, request, *args, **kwargs):
#         if 'vendor_id' in kwargs:
#             self.vendor_obj = Vendor.objects.get(id=kwargs['vendor_id'])
#             print(f"Using {self.vendor_obj.name}")
#         else:
#             print('Error: no vendor_id')
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['today'] = date.today().strftime('%Y-%m-%d')
#         data['vendor_obj'] = self.vendor_obj
#         return data

#     def get_form_kwargs(self):
#         kwargs = super(NewExpenseByVendorModal, self).get_form_kwargs()
#         kwargs.update({
#             'vendor_obj': self.vendor_obj,
#             })
#         return kwargs

class NewExpense(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new expense modal"""
    permission_required = ('ledger.add_expense', )
    template_name = 'ledger/new_expense.html'
    form_class = NewExpenseForm
    success_url = reverse_lazy('ledger:ExpenseList')
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
        kwargs = super(NewExpense, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            })
        return kwargs

class NewExpenseModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new expense modal"""
    permission_required = ('ledger.add_expense', )
    template_name = 'ledger/new_expense_modal.html'
    form_class = NewExpenseModalForm
    success_url = reverse_lazy('ledger:ExpenseList')
    vendor_obj = None

    def dispatch(self, request, *args, **kwargs):
        vendor_id = request.GET.get('q')
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
        kwargs = super(NewExpenseModal, self).get_form_kwargs()
        kwargs.update({
            'vendor_obj': self.vendor_obj,
            })
        return kwargs


@login_required
@permission_required('ledger.add_expense',)
def NewExpenseSelectVendorView(request, *args, **kwargs):
    """Select Vendor for New Expense"""
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
            template_name='ledger/_new_expense_choose_vendor.html',
            context={
                'vendor_list': object_list,
                }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "ledger/new_expense_view.html", {'vendors': vendors, 'vendor_obj': vendor_obj})

@login_required
@permission_required('ledger.view_expense')
def ExpenseExportCsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Expected_date', 'Entry_date', 'Amount', 'Category', 'Payee', 'Payment_method', 'Payment_ref', 'Invoice_date', 'Invoice_no', 'Description', 'Remarks'])

    expenses = Expense.objects.all().values_list('expected_date', 'entry_date', 'amount', 'category', 'payee', 'payment_method', 'payment_ref', 'invoice_date', 'invoice_no', 'description', 'remarks')
    for expense in expenses:
        writer.writerow(expense)

    return response