from datetime import date
import csv
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from bootstrap_modal_forms.generic import BSModalUpdateView
from .models import (
    ExpenseCategory,
    Expense
)

from .forms import (
    NewExpenseCategoryForm, ExpenseCategoryUpdateForm,
    NewExpenseForm, ExpenseUpdateForm,
    ExpenseUpdateModalForm,
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

class ExpenseCategoryUpdate(UpdateView, LoginRequiredMixin):
    model = ExpenseCategory
    form_class = ExpenseCategoryUpdateForm
    template_name = "ledger/expense_category_update.html"
    success_url = reverse_lazy('ledger:ExpenseCategoryList')

class ExpenseCategoryDelete(DeleteView, LoginRequiredMixin):
    model = ExpenseCategory
    template_name = "ledger/expense_category_confirm_delete.html"
    success_url = reverse_lazy('ledger:ExpenseCategoryList')

class NewExpenseCategory(CreateView, LoginRequiredMixin):
    """Add new vendor"""
    model = ExpenseCategory
    template_name = 'ledger/new_expense_category.html'
    form_class = NewExpenseCategoryForm
    success_url = reverse_lazy('ledger:ExpenseCategoryList')

# Expense Views
# =============

class ExpenseList(ListView, LoginRequiredMixin):
    model = Expense
    template_name = "ledger/expense_list.html"
    context_object_name = 'expense_list_obj'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
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
        return object_list

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['last_query'] = self.last_query
        data['last_query_count'] = self.last_query_count
        return data

class ExpenseDetail(DetailView, LoginRequiredMixin):
    model = Expense
    template_name = "ledger/expense_detail.html"
    context_object_name = "expense_obj"

class ExpenseUpdate(UpdateView, LoginRequiredMixin):
    model = Expense
    form_class = ExpenseUpdateForm
    template_name = "ledger/expense_update.html"

    def get_success_url(self):
        return reverse('ledger:ExpenseDetail', args=(self.object.pk,))

class ExpenseUpdateModal(BSModalUpdateView, LoginRequiredMixin):
    model = Expense
    template_name = 'ledger/expense_update_modal.html'
    form_class = ExpenseUpdateModalForm
    success_message = 'Success: Book was updated.'
    success_url = reverse_lazy('ledger:ExpenseList')

class ExpenseDelete(DeleteView, LoginRequiredMixin):
    model = Expense
    template_name = "ledger/expense_confirm_delete.html"
    success_url = reverse_lazy('ledger:ExpenseList')

class NewExpense(CreateView, LoginRequiredMixin):
    model = Expense
    template_name = 'ledger/new_expense.html'
    form_class = NewExpenseForm
    success_url = reverse_lazy('ledger:ExpenseList')
    vendor_obj = None
    
    def dispatch(self, request, *args, **kwargs):
        if 'vendor' in kwargs:
            self.vendor_obj = Vendor.objects.get(id=kwargs['vendor'])
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

def ExpenseExportCsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Expected_date', 'Settled_date', 'Entry_date', 'Amount', 'Category', 'Payee', 'Payment_method', 'Payment_ref', 'Invoice_date', 'Invoice_no', 'Description', 'Remarks'])

    expenses = Expense.objects.all().values_list('expected_date', 'settled_date', 'entry_date', 'amount', 'category', 'payee', 'payment_method', 'payment_ref', 'invoice_date', 'invoice_no', 'description', 'remarks')
    for expense in expenses:
        writer.writerow(expense)

    return response