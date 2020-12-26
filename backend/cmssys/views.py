from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import (
    AuditLog,
)
# Create your views here.

class AuditLogList(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    """
    Displays AuditLog
    """
    INV_ITEM='1'
    INV_MOVE_LOG='2'
    DEPLETION='3'
    DEPLETION_ITEM='4'
    CLASS_TYPE_CHOICES = [
        (INV_ITEM, 'InventoryItem'),
        (INV_MOVE_LOG, 'InventoryMovementLog'),
        (DEPLETION, 'Depletion'),
        (DEPLETION_ITEM, 'DepletionItem'),
    ]
    permission_required = ('cmssys.view_auditlog',)
    template_name = 'cmssys/audit_log.html'
    model = AuditLog
    context_object_name = 'audit_log'
    paginate_by = 20
    last_query = ''
    last_query_count = 0

    def get_queryset(self):
        self.begin = self.request.GET.get('begin')
        self.end = self.request.GET.get('end')
        self.disp_type = self.request.GET.get('t') or ''
        if self.disp_type:
            class_type = dict(self.CLASS_TYPE_CHOICES).get(self.disp_type)
            object_list = AuditLog.objects.filter(class_name=class_type).order_by('-last_updated')
        else:
            object_list = AuditLog.objects.all().order_by('-last_updated')
        query = self.request.GET.get('q')
        if query:
            self.last_query = query
            object_list = object_list.filter(
                Q(class_name__icontains=query) |
                Q(property_name__icontains=query) |
                Q(event_name__icontains=query)
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