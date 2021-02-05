
from django.utils import timezone
import pytz
from django.conf import settings
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
    PaymentDetails,
    PaymentMethod,
)
from cmssys.models import Encounter

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
        today = timezone.now()
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
        elif self.day:
            try:
                seldate = datetime.strptime(self.day, "%Y%m%d")
            except:
                seldate = today
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

class PaymentsToday(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Lists billing and payments for the day
    """
    PERIOD_CHOICES = [
        ('a', 'AM'),
        ('p', 'PM'),
    ]
    PERIOD_CUTOFF_HR = 15  # 3pm in 24hr time
    PERIOD_CUTOFF_MIN = 0
    RECENT_BILLS = 100
    permission_required = ('cmsinv.view_payment',)
    template_name = 'cmsacc/payments_today.html'
    model = PaymentDetails
    context_object_name = 'payment_list'
    paginate_by = 50
    period = None
    lastdate = None
    session_stats = None

    def get_queryset(self):
        self.period = self.request.GET.get('p') or None
        self.day = self.request.GET.get('d') or None
        today = timezone.now()
        self.lastdate = today - timedelta(days=1)
        # Cycle through recent bills
        recent_bills = PaymentDetails.objects.order_by('-date_created')[:self.RECENT_BILLS]
        recent_dates = set()
        for bill in recent_bills:
            recent_dates.add(bill.date_created.strftime('%Y-%m-%d'))
        while not self.lastdate.strftime('%Y-%m-%d') in recent_dates:
            self.lastdate = self.lastdate - timedelta(days=1)
        if self.day == '1':  # Last encounter date before today
            seldate = self.lastdate
        elif self.day:
            try:
                seldate = datetime.strptime(self.day, "%Y%m%d")
            except:
                seldate = today
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
            object_list = PaymentDetails.objects.filter(
                bill__encounter__date_created__icontains=query_date,
                bill__encounter__date_created__lt=time_cutoff
            ).order_by('-date_created', '-last_updated')
        elif self.period == 'p':
            object_list = PaymentDetails.objects.filter(
                bill__encounter__date_created__icontains=query_date,
                bill__encounter__date_created__gte=time_cutoff
            ).order_by('-date_created', '-last_updated')
        else:
            object_list = object_list = PaymentDetails.objects.filter(
            bill__encounter__date_created__icontains=query_date
        ).order_by('-date_created', '-last_updated')
        object_list = object_list.exclude(
            Q(bill__encounter__patient__patient_no='00AM')|
            Q(bill__encounter__patient__patient_no='00PM')
        )
        self.session_stats = object_list.aggregate(
            count=Count('bill__encounter__id'),
            bill_total=Sum('bill__total'),
            unbalance_total=Sum('bill__unbalance_amt'),

        )
        self.session_stats['cash_total'] = object_list.filter(
            payment_method__payment_method='Cash'
        ).aggregate(Sum('paid_amt'))['paid_amt__sum'] or 0.0
        self.session_stats['other_total'] = object_list.exclude(
            payment_method__payment_method='Cash'
        ).aggregate(Sum('paid_amt'))['paid_amt__sum'] or 0.0

        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['day'] = self.day
        context['period'] = self.period
        context['session_stats'] = self.session_stats
        context['lastdate'] = self.lastdate.strftime("%Y-%m-%d")
        return context
    