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

from .models import (
    Bill,
    BillDetail,
    Cashbook,
)
# class MonthlyBillingList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
#     """
#     Lists monthly CMS billing
#     """
#     permission_required = ('cmsinv.view_bill',)
#     template_name = 'cmsinv/monthly_bill_list.html'
#     model = InventoryItem
#     context_object_name = 'match_item_list_obj'
#     paginate_by = 20
#     last_query = ''
#     last_query_count = 0

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         self.invtype = self.request.GET.get('invtype') or '0'
#         self.status = self.request.GET.get('status') or ''
#         self.dd = self.request.GET.get('dd') or 'any'
#         if query:
#             self.last_query = query
#             object_list = InventoryItem.objects.filter(
#                 Q(registration_no__icontains=query) |
#                 Q(product_name__icontains=query) |
#                 # Q(generic_name__icontains=query) |
#                 Q(alias__icontains=query) |
#                 # Q(clinic_drug_no__icontains=query) |
#                 Q(ingredient__icontains=query)
#             ).order_by('discontinue')
#         else:
#             self.last_query = ''
#             object_list = InventoryItem.objects.all().order_by('discontinue')
#         if self.status == '1':
#             object_list = object_list.filter(discontinue=False)
#         elif self.status == '0':
#             object_list = object_list.filter(discontinue=True)
#         if self.invtype =='1':
#             object_list = object_list.filter(inventory_type='Drug')
#         elif self.invtype == '2':
#             object_list = object_list.filter(inventory_type='Supplement')
#         if self.dd == '1':
#             object_list = object_list.filter(dangerous_sign=True)
#         elif self.dd == '0':
#             object_list = object_list.filter(dangerous_sign=False)
#         self.last_query_count = object_list.count
#         return object_list

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['last_query'] = self.last_query
#         data['last_query_count'] = self.last_query_count
#         data['invtype'] = self.invtype
#         data['status'] = self.status
#         data['dd'] = self.dd
#         return data

class CashbookToday(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists monthly CMS billing
    """
    PERIOD_CHOICES = [
        ('a', 'AM'),
        ('p', 'PM'),
    ]
    PERIOD_CUTOFF_HR = 15  # 3pm in 24hr time
    PERIOD_CUTOFF_MIN = 0
    permission_required = ('cmsinv.view_cashbook',)
    template_name = 'cmsacc/cashbook_today.html'
    model = Cashbook
    context_object_name = 'cashbook_obj'
    paginate_by = 50
    begin = None
    end = None
    period = None

    def get_queryset(self):
        self.period = self.request.GET.get('p') or None
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        now = datetime.today()
        print(now)
        today_date = now.strftime('%Y-%m-%d')
        today_cutoff = now.replace(hour=self.PERIOD_CUTOFF_HR, minute=self.PERIOD_CUTOFF_MIN)
        # current_time = timezone.now().strftime('%H:%m')
        if not self.period:
            if now >= today_cutoff:
                self.period = 'p'
            else:
                self.period = 'a'
        object_list = Cashbook.objects.filter(
            date_created__icontains=today_date
        )
        if self.period == 'a':
            object_list.filter(
                date_created__lt=today_cutoff
            ).order_by('date_created')
        elif self.period == 'p':
            object_list.filter(
                date_created__gte=today_cutoff
            ).order_by('date_created')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self.period
        return context
    