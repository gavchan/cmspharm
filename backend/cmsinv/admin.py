from django.contrib import admin
from .models import ( 
    Advisory, Supplier, Instruction,
    InventoryItemType, InventoryItem, InventoryMovementLog,
    Request, RequestItem, Delivery, ReceivedItem,
    Depletion, DepletionItem, #DepletionDepletionItem
)

class CMSModelAdmin(admin.ModelAdmin):

    # A handy constant for the name of the alternate database.
    using = 'cms_db'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'cms_db' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'cms_db' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'cms_db' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'cms_db' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'cms_db' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

admin.site.register(Advisory, CMSModelAdmin)
admin.site.register(Instruction, CMSModelAdmin)
admin.site.register(Supplier, CMSModelAdmin)
admin.site.register(InventoryItem, CMSModelAdmin)
admin.site.register(InventoryItemType, CMSModelAdmin)
admin.site.register(InventoryMovementLog, CMSModelAdmin)
admin.site.register(Request, CMSModelAdmin)
admin.site.register(RequestItem, CMSModelAdmin)
admin.site.register(Delivery, CMSModelAdmin) 
admin.site.register(ReceivedItem, CMSModelAdmin)
admin.site.register(Depletion, CMSModelAdmin)
admin.site.register(DepletionItem, CMSModelAdmin)
# admin.site.register(DepletionDepletionItem, CMSModelAdmin)