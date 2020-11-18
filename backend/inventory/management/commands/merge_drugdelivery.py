import csv, os, sys
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from cmsinv.models import InventoryItem
from drugdb.models import RegisteredDrug, DrugDelivery
from inventory.models import Item, ItemType, Delivery, DeliveryOrder, DeliveryItem, Category
from django.conf import settings

class Command(BaseCommand):
    """
    Migrates Drug Delivery records into DeliveryOrder/DeliveryItems
    """
    help = 'Migrate Drug Delivery records into DeliveryOrder/DeliveryItems'
    item_obj = None
    delivery_obj = None
    delivery_item_obj = None
    expense_obj = None

    def compare(self, drugfield, itemfield):
        """
        Compares drugfield and itemfield, if not matching and not empty,
        prompt for selection
        """
        if drugfield == itemfield:
            return itemfield
        else:
            print(f"-- 1. Drugfield: {drugfield} |2. Itemfield: {itemfield}")
            if not drugfield:
                return itemfield
            elif not itemfield:
                return drugfield
            else:
                # Drugfield and Itemfield both not empty, prompt for selection
                choice = ""
                while (choice != "1" or choice != "2"):
                    choice = input("-- Select 1 or 2 to use: ")
                if choice == "1":
                    return drugfield
                elif choice == "2":
                    return itemfield

        #         reg_drug = RegisteredDrug.objects.get(reg_no=cmsinv_item.registration_no)
        #     except RegisteredDrug.DoesNotExist:
        #         reg_drug = None
        #         note = 'No matching reg_no'
        #     item = {
        #         'name': cmsinv_item.product_name,
        #         'cmsid': cmsinv_item.id,
        #         'item_type': item_type,
        #         'reg_drug': cmsinv_item.registration_no,
        #         'note': note,
        #         'is_active': not cmsinv_item.discontinue,
        #     }
        #     new_item, created = Item.objects.update_or_create(cmsid=cmsinv_item.id, defaults=item)
        #     if created:
        #         count += 1
        #         self.stdout.write(f"Created id:{new_item.id} from cms:{cmsinv_item.id} | {cmsinv_item.product_name}")
        #     else:
        #         print(f"Update CMS {cmsinv_item.id} Reg # {cmsinv_item.registration_no}")
        # print(f"Created {count} item records.")
        
    def handle(self, *args, **options):

        # Iterate through DrugDelivery objects, create equivalent DeliveryOrder/DeliveryItem objects

        drugdeliveries = DrugDelivery.objects.all().order_by('id')[:1000]
        item_type = ItemType.objects.get(value='1')
        category = Category.objects.get(value='1')
        count = 0
        matching = 0
        new_items = 0
        new_delivery_items = 0
        new_delivery_orders = 0
        for drugdel in drugdeliveries:
            self.item_obj = None
            count += 1
            print(f"Processing DrugDelivery #{drugdel.id:5} reg_no {drugdel.reg_no}")
            # Get related Item or create if not exists
            try:
                self.item_obj = Item.objects.get(reg_no=drugdel.reg_no)
            except Item.DoesNotExist:
                print(f"--No Item with matching reg_no")
            try:
                cmsitem = InventoryItem.objects.get(registration_no=drugdel.reg_no)
            except InventoryItem.DoesNotExist:
                print(f"--No CMS InventoryItem with matching reg_no")
            if self.item_obj:
                # Matching Item (reg_no) - Check for matching name, cmsid if exists
                matching += 1
                self.item_obj.name = self.compare(drugdel.product_name, self.item_obj.name)
                print(self.item_obj.name)
                if drugdel.cmsinv_item:
                    self.item_obj.cmsid = self.compare(drugdel.cmsinv_item.id, self.item_obj.cmsid)
                    print(self.item_obj.cmsid)
            elif cmsitem:
                # No matching Item but matches CMS Inventory Item (reg_no)
                # ==> Add new Item that matches CMS Inventory Item
                new_item_data = {
                    'name': cmsitem.product_name,
                    'item_type': item_type,
                    'category': category,
                    'reg_no': cmsitem.registration_no,
                    'is_active': True,
                }
                self.item_obj, created = Item.objects.update_or_create(cmsid=cmsitem.id, defaults=new_item_data)
                if created:
                    new_items += 1
                    print(f"--Add new Item from cmsitem: {self.item_obj.name}")
            else:
                # No matching Item, no matching CMS Inventory Item
                new_item_data = {
                    'name': drugdel.product_name,
                    'item_type': item_type,
                    'category': category,
                    'reg_no': drugdel.reg_no,
                    'is_active': True,
                }
                if drugdel.cmsinv_item:
                    new_item_data['cmsid'] = drugdel.cmsinv_item.id
                self.item_obj = Item.objects.create(**new_item_data)
                new_items += 1
                print("--Add new Item from DrugDelivery record")
                # Create if does not exist
            
            # Create DeliveryOrder and match Expense (Bill)
            self.expense_obj = drugdel.bill or None
            if not self.expense_obj:
                print("--Missing bill/expense data")
            else:
                print(f"Expense #{self.expense_obj.id:3}|{self.expense_obj.payee} - {self.expense_obj.amount} ")
                new_delivery_order_data = {
                    'invoice_no': self.expense_obj.invoice_no,
                    'invoice_date': self.expense_obj.invoice_date,
                    'received_date': drugdel.received_date,
                    'vendor': self.expense_obj.vendor,
                    'amount': self.expense_obj.amount,
                    'is_paid': True,
                    'bill': self.expense_obj,
                    'due_date': None,
                    'other_ref': self.expense_obj.other_ref,
                    'remarks': self.expense_obj.remarks,
                    'date_created': self.expense_obj.date_created,
                    'last_updated': self.expense_obj.last_updated,
                }
                self.delivery_obj, created = DeliveryOrder.objects.get_or_create(
                    bill=self.expense_obj, 
                    defaults=new_delivery_order_data
                )

                if created:
                    new_delivery_orders += 1
                    print(f"--Added new DeliveryOrder record: {self.delivery_obj.id} ${self.delivery_obj.amount}")
                else:
                    print(f'--Found existing DeliveryOrder record: {self.delivery_obj.id} ${self.delivery_obj.amount}')
                # Create DeliveryItem
                if drugdel.expiry_date:
                    expiry_month = drugdel.expiry_date.strftime("%Y%m%d")
                else:
                    expiry_month = ""
                new_delivery_item_data = {
                    'item': self.item_obj,
                    'delivery_order': self.delivery_obj,
                    'purchase_quantity': drugdel.purchase_quantity,
                    'purchase_unit': drugdel.purchase_unit,
                    'bonus_quantity': drugdel.bonus_quantity,
                    'unit_price': drugdel.unit_price,
                    'discount': drugdel.discount,
                    'items_per_purchase': drugdel.items_per_purchase,
                    'batch_num': drugdel.batch_num,
                    'other_ref': drugdel.other_ref,
                    'expiry_month': expiry_month,
                }
                self.delivery_item_obj = DeliveryItem(**new_delivery_item_data)
                self.delivery_item_obj.save()
                new_delivery_items += 1
                print(f"--Add new DeliveryItem record: {self.delivery_item_obj.id}")

        print(f"Processed: {count}, Matching: {matching}, ",
            f"New DeliveryOrders: {new_delivery_orders}, New DeliveryItems: {new_delivery_items}")

    # ---- Delivery Object
    # product_name = models.CharField(max_length=255)
    # vendor = models.CharField(max_length=255, blank=True, null=True)
    # delivery_note_no = models.CharField(max_length=255, blank=True, null=True)
    # # delivery_note_no: can be referenced to cmsinv.Delivery; a.k.a. invoice no.
    # purchase_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    # purchase_unit = models.CharField(max_length=100, choices=PURCHASE_UNIT_CHOICES, default=PACK)
    # bonus_quantity = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    # unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    # # discount: percentage discount applied to unit_price in calculation of total; e.g. 25 = 25% off
    # items_per_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    # # items_per_purchase: number of granular items per unit of purchase. E.g. 1 pack can contain 100 items
    # # items_unit: defined in respective model (ConsumableDelivery, DrugDelivery)
    # batch_num = models.CharField(max_length=100, blank=True, null=True)
    # other_ref = models.CharField(max_length=100, blank=True, null=True)
    # remark = models.CharField(max_length=255, blank=True, null=True)
    # received_date = models.DateField()
    # received_by = models.CharField(max_length=255, blank=True, null=True)
    # expiry_month = models.CharField(max_length=8, default="", blank=True, null=True)
    # # expiry_month: format of yyyymm, or yyyymmdd; to supercede expiry_date
    # expiry_date = models.DateField(blank=True, null=True)
    # date_created = models.DateTimeField(auto_now_add=True)
    # version = models.PositiveIntegerField(default=1)
    # last_updated = models.DateTimeField(auto_now=True)
    # ---- DrugDelivery Object (inherits from Delivery)
    # reg_no = models.CharField(max_length=255, blank=True, null=True)
    # cmsinv_item = models.ForeignKey(
    #     InventoryItem, on_delete=models.PROTECT,
    #     blank=True, null=True,
    #     )
    # bill = models.ForeignKey(
    #     Expense, on_delete=models.PROTECT,
    #     blank=True, null=True,
    # )
    # items_unit = models.CharField(max_length=100, choices=ITEMS_UNIT_CHOICES, default=TAB)