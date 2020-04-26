from django.contrib import admin
from .models import ItemType, Category, Item, ItemsUnit, Vendor, ItemDelivery

admin.site.register(ItemType)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(ItemsUnit)
admin.site.register(Vendor)
admin.site.register(ItemDelivery)