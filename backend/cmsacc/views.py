
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy, resolve, Resolver404
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.db.models import Q, Sum, Count

from .models import (
    Bill,
    BillDetail,
    Cashbook,
)
from cmssys.models import Encounter
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
            ).order_by('-date_created', '-last_updated')
        elif self.period == 'p':
            object_list.filter(
                date_created__gte=today_cutoff
            ).order_by('-date_created', '-last_updated')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self.period
        return context

class BillToday(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists monthly CMS billing
    """
    PERIOD_CHOICES = [
        ('a', 'AM'),
        ('p', 'PM'),
    ]
    PERIOD_CUTOFF_HR = 15  # 3pm in 24hr time
    PERIOD_CUTOFF_MIN = 0
    RECENT_BILLS = 250
    permission_required = ('cmsinv.view_bill',)
    template_name = 'cmsacc/bill_today.html'
    model = Cashbook
    context_object_name = 'bill_obj_list'
    paginate_by = 50
    period = None
    lastdate = None
    session_stats = None

    def get_queryset(self):
        self.period = self.request.GET.get('p') or None
        self.day = self.request.GET.get('d') or None
        today = datetime.today()
        self.lastdate = today - timedelta(days=1)

        # Cycle through recent bills
        recent_bills = Encounter.objects.order_by('-date_created')[:self.RECENT_BILLS]
        recent_dates = set()
        for bill in recent_bills:
            recent_dates.add(bill.date_created.strftime('%Y-%m-%d'))
        while not self.lastdate.strftime('%Y-%m-%d') in recent_dates:
            self.lastdate = self.lastdate - timedelta(days=1)
        if self.day == '1':  # Last encounter date before today
            seldate = self.lastdate
        else:
            seldate = today
        query_date = seldate.strftime('%Y-%m-%d')
        time_cutoff = seldate.replace(hour=self.PERIOD_CUTOFF_HR, minute=self.PERIOD_CUTOFF_MIN)
        if not self.period:
            if seldate >= time_cutoff:
                self.period = 'p'
            else:
                self.period = 'a'
        if self.period == 'a':
            object_list = Bill.objects.filter(
                encounter__date_created__icontains=query_date,
                encounter__date_created__lt=time_cutoff
            ).order_by('-encounter.date_created', '-last_updated')
        elif self.period == 'p':
            object_list = Bill.objects.filter(
                encounter__date_created__icontains=query_date,
                encounter__date_created__gte=time_cutoff
            ).order_by('-encounter.date_created', '-last_updated')
        else:
            object_list = object_list = Bill.objects.filter(
            encounter__date_created__icontains=query_date
        )
        object_list = object_list.exclude(
            Q(encounter__patient__patient_no='00AM')|
            Q(encounter__patient__patient_no='00PM')
        )
        self.session_stats = object_list.aggregate(
            count=Count('total'),
            sumtotal=Sum('total')
        )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['day'] = self.day
        context['period'] = self.period
        context['session_stats'] = self.session_stats
        context['lastdate'] = self.lastdate.strftime("%Y-%m-%d")
        return context
    