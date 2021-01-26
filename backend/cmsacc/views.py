
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
    local_timezone = pytz.timezone(settings.TIME_ZONE)

    def get_queryset(self):
        self.period = self.request.GET.get('p') or None
        self.day = self.request.GET.get('d') or None
        # today = datetime.today().astimezone(self.local_timezone)
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
        else:
            seldate = today
        query_date = seldate.strftime('%Y-%m-%d')
        time_cutoff = seldate.replace(hour=self.PERIOD_CUTOFF_HR, minute=self.PERIOD_CUTOFF_MIN)
        print(f"Today:{today}; Cutoff: {time_cutoff}")
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
    