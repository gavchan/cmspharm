from django.contrib import admin
from .models import (
    Category, Item, ItemsUnit, Vendor,
    DeliveryOrder, DeliveryItem,
)
admin.site.register(Category)
admin.site.register(DeliveryOrder)
admin.site.register(DeliveryItem)
admin.site.register(Item)
admin.site.register(ItemsUnit)
admin.site.register(Vendor)