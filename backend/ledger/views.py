import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy, resolve, Resolver404
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from .models import (
    ExpenseCategory,
    Expense,
    IncomeSource,
    Income,
)
from inventory.models import (
    DeliveryOrder,
)
from .forms import (
    NewExpenseCategoryForm, ExpenseCategoryUpdateForm,
    NewExpenseForm, ExpenseUpdateForm,
    ExpenseUpdateModalForm,
    # NewExpenseByVendorModalForm,
    NewExpenseModalForm,
    DeliveryPaymentModalForm,
    NewIncomeModalForm,
    IncomeUpdateModalForm,
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
    today =  datetime.today().strftime('%Y-%m-%d')
    begin = ''
    end = ''

    def get_queryset(self):
        query = self.request.GET.get('q')
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
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
    next_url = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('next'):
            self.next_url = self.request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['expense_obj'] = self.object
        return data

    def get_success_url(self):
        try:
            resolve(self.next_url)
        except Resolver404:
            return reverse('ledger:ExpenseDetail', args=(self.object.pk,))
        return self.next_url

class ExpenseUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Expense"""
    permission_required = ('ledger.change_expense',)
    model = Expense
    form_class = ExpenseUpdateModalForm
    template_name = "ledger/expense_update_modal.html"
    success_message = 'Success: Expense was updated'
    next_url = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('next'):
            self.next_url = self.request.GET.get('next')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['expense_obj'] = self.object
        return data

    def get_success_url(self):
        try:
            resolve(self.next_url)
        except Resolver404:
            return reverse('ledger:ExpenseDetail', args=(self.object.pk,))
        return self.next_url


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
#         data['today'] = datetime.today().strftime('%Y-%m-%d')
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
        data['today'] = datetime.today().strftime('%Y-%m-%d')
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
        vendor_id = request.GET.get('vendor')
        if vendor_id:
            self.vendor_obj = Vendor.objects.get(id=vendor_id)
        else:
            self.vendor_obj = None
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = datetime.today().strftime('%Y-%m-%d')
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

class DeliveryPaymentModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new expense modal"""
    permission_required = ('ledger.add_expense', )
    template_name = 'ledger/delivery_payment_modal.html'
    form_class = DeliveryPaymentModalForm
    vendor_obj = None
    existing_bill = False

    def dispatch(self, request, *args, **kwargs):
        if 'delivery_id' in kwargs:
            self.delivery_obj = DeliveryOrder.objects.get(id=kwargs['delivery_id'])
        else:
            print("Error: no delivery_obj")
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = datetime.today().strftime('%Y-%m-%d')
        data['delivery_obj'] = self.delivery_obj
        return data

    def get_form_kwargs(self):
        kwargs = super(DeliveryPaymentModal, self).get_form_kwargs()
        kwargs.update({
            'delivery_obj': self.delivery_obj,
            })
        return kwargs

    def get_success_url(self):
        return reverse('ledger:ExpenseDetail', args=(self.object.id,))

    def form_valid(self, form):
        self.object = form.save()
        self.delivery_obj.bill = self.object
        self.delivery_obj.is_paid = True
        self.delivery_obj.save()
        return HttpResponseRedirect(self.get_success_url())

class ExpenseDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Show Expense Details for Drug Category, allow add delivery"""
    permission_required = ('ledger.view_expense',)
    template_name = 'ledger/expense_detail.html'
    model = Expense
    deliveryorder_list = None
    unpaid_deliveries_list = None
    list_total = 0

    def dispatch(self, request, *args, **kwargs):
        self.expense_obj = Expense.objects.get(id=kwargs['pk']) 
        try:
            self.deliveryorder_list = DeliveryOrder.objects.filter(bill=self.expense_obj.id)
        except:
            print("No delivery orders")
        if self.deliveryorder_list:
            self.list_total = self.deliveryorder_list.aggregate(Sum('amount'))
        else:
            self.list_total = 0
        self.unpaid_deliveries_list = DeliveryOrder.objects.filter(vendor=self.expense_obj.vendor, is_paid=False) or None
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['today'] = datetime.today().strftime('%Y-%m-%d')
        detail_list = [] 
        for order in self.deliveryorder_list.all():
            delivery_detail = {
                'id': order.id,
                'invoice_date': order.invoice_date,
                'invoice_no': order.invoice_no,
                'received_date': order.received_date,
                'amount': order.amount,
                'is_paid': order.is_paid,
                'cms_synced': order.cms_synced,
            }
            delivery_detail['items'] = []
            count = 0
            for deliveryitem in order.delivery_items.all():
                item_detail = {
                    'id': deliveryitem.id,
                    'name': deliveryitem.item.name,
                    'items_per_purchase': deliveryitem.items_per_purchase,
                    'items_unit': deliveryitem.items_unit,
                    'purchase_unit': deliveryitem.purchase_unit,
                    'purchase_quantity': deliveryitem.purchase_quantity,
                    'bonus_quantity': deliveryitem.bonus_quantity,
                    'standard_cost': deliveryitem.standard_cost,
                    'average_cost': deliveryitem.average_cost,
                    'total_price': deliveryitem.total_price,
                }
                count += 1
                delivery_detail['items'].append(item_detail)
                delivery_detail['items_count'] = count
            detail_list.append(delivery_detail)
        data['deliveryorder_list'] = detail_list
        data['unpaid_deliveries_list'] = self.unpaid_deliveries_list
        data['expense_obj'] = self.expense_obj
        if self.deliveryorder_list:
            data['list_total'] = self.list_total['amount__sum']
        return data

@login_required
@permission_required('ledger.change_expense', 'inventory.change_deliveryorder')
def ExpenseAddDeliveryOrder(request, *args, **kwargs):
    expense_obj = Expense.objects.get(pk=kwargs['expense_id']) or None
    delivery_obj = DeliveryOrder.objects.get(pk=kwargs['delivery_id']) or None
    # Check if existing invoice_no
    
    if expense_obj and delivery_obj:
        if delivery_obj.invoice_no in expense_obj.invoice_no:
            print(f"Error: Invoice {delivery_obj.invoice_no} already exists in expense record.")
        else:
            # Update delivery_obj
            delivery_obj.bill = expense_obj
            delivery_obj.is_paid = True
            delivery_obj.save()
            # Update expense_obj invoice_no
            if expense_obj.invoice_no:
                new_invoice_no = ','.join([expense_obj.invoice_no, delivery_obj.invoice_no])
                expense_obj.invoice_no = new_invoice_no
            else:
                expense_obj.invoice_no = delivery_obj.invoice_no    
            expense_obj.save()
            print(f"Delivery #{delivery_obj.id} added to expense #{expense_obj.id}")
    return HttpResponseRedirect(reverse('ledger:ExpenseDetail', args=(expense_obj.id,)))

@login_required
@permission_required('ledger.change_expense', 'inventory.change_deliveryorder')
def ExpenseRemoveDeliveryOrder(request, *args, **kwargs):
    expense_obj = Expense.objects.get(pk=kwargs['expense_id']) or None
    delivery_obj = DeliveryOrder.objects.get(pk=kwargs['delivery_id']) or None
    if expense_obj and delivery_obj:
        delivery_obj.bill = None
        delivery_obj.is_paid = False
        delivery_obj.save()
        # Update expense_obj invoice_no
        invoice_nums = expense_obj.invoice_no.split(',')
        removed_invoice_no = invoice_nums.pop(invoice_nums.index(delivery_obj.invoice_no))
        if len(invoice_nums) > 1:
            expense_obj.invoice_no = ','.join(invoice_nums)
        elif len(invoice_nums) == 1:
            expense_obj.invoice_no = invoice_nums[0]
        else:
            expense_obj.invoice_no = ''
        expense_obj.save()
        print(f"Delivery #{delivery_obj.id} #{removed_invoice_no} removed from expense #{expense_obj.id}")
    return HttpResponseRedirect(reverse('ledger:ExpenseDetail', args=(expense_obj.id,)))

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

@login_required
@permission_required('ledger.change_expense')
def ExpenseConfirmPermanentModalView(request, *args, **kwargs):
    if kwargs['pk']:
        expense_obj = get_object_or_404(Expense, pk=kwargs['pk'])
    else:
        print("Error: no expense pk")
    uri = request.GET.get('next', reverse('ledger:ExpenseDetail', args=(expense_obj.id,)))
    session_id = request.session.session_key

    context = {
        'expense_obj': expense_obj
    }
    # If POST request confirms make permament, set permanent flag
    if request.method == 'POST':
        expense_obj.permanent = True
        expense_obj.save()
        return redirect(uri)

    return render(request, "ledger/expense_confirm_permanent_modal.html", context)

class IncomeDetail(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    """Show Income Details for Drug Category, allow add delivery"""
    permission_required = ('ledger.view_income',)
    template_name = 'ledger/income_detail.html'
    model = Income
    context_object_name = 'income_obj'

class IncomeDeleteModal(BSModalDeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Income modal"""
    permission_required = ('ledger.delete_income',)
    model = Income
    template_name = 'ledger/income_confirm_delete_modal.html'
    success_message = 'Success: Income record was deleted.'
    success_url = reverse_lazy('ledger:IncomeList')

class IncomeList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """Lists Income"""
    permission_required = ('ledger.view_income')
    model = Income
    template_name = "ledger/income_list.html"
    context_object_name = 'income_list_obj'
    paginate_by = 20
    last_query = ''
    last_query_count = 0
    today =  datetime.today().strftime('%Y-%m-%d')
    begin = ''
    end = ''

    def get_queryset(self):
        query = self.request.GET.get('q')
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        if query:
            self.last_query = query
            object_list = Income.objects.filter(
                Q(payer__icontains=query)
            ).order_by('-expected_date')
            self.last_query_count = object_list.count
        else:
            self.last_query = ''
            object_list = Income.objects.all().order_by('-expected_date')
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

class NewIncomeModal(BSModalCreateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Add new income modal"""
    permission_required = ('ledger.add_income', )
    template_name = 'ledger/new_income_modal.html'
    form_class = NewIncomeModalForm
    success_url = reverse_lazy('ledger:IncomeList')


class IncomeUpdateModal(BSModalUpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    """Update Income"""
    permission_required = ('ledger.change_income',)
    model = Income
    form_class = IncomeUpdateModalForm
    template_name = "ledger/income_update_modal.html"
    success_message = 'Success: Income was updated'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['income_obj'] = self.object
        return data