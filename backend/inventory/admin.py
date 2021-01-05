from django.contrib import admin
from .models import (
    Category, Item, ItemType, Vendor,
    DeliveryOrder, DeliveryItem,
)
from .custom_filters import DuplicateItemCmsidFilter

class ItemAdmin(admin.ModelAdmin):
    list_filter = (DuplicateItemCmsidFilter, )

admin.site.register(Category)
admin.site.register(DeliveryOrder)
admin.site.register(DeliveryItem)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemType)
admin.site.register(Vendor)