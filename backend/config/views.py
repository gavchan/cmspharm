from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from inventory.models import (
    Vendor,
)
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse


@login_required
@permission_required('inventory.add_deliveryorder',)
def HomeSelectVendorView(request, *args, **kwargs):
    """Select Vendor for New DeliveryOrder or Expense"""
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
            template_name='inventory/_choose_vendor.html',
            context={
                'vendor_list': object_list,
                }
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "home.html", {'vendors': vendors, 'vendor_obj': vendor_obj})

