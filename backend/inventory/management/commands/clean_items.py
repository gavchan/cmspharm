import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug, Company, Ingredient
from cmsinv.models import (
    InventoryItem, Prescription, PrescriptionDetail, InventoryMovementLog,
    DepletionItem, ReceivedItem
)
from inventory.models import (
    Item, DeliveryItem,
)
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Cleans Item database - mark unused items for Trash
    """
    help = 'Cleans Item database - mark unused items for Trash'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--delete', action='store_true', help='Mark and delete')
        parser.add_argument('-r', '--remove', action='store_true', help='Remove marked/trashed')
        
    def handle(self, *args, **kwargs):
        delete_flag = kwargs['delete'] or False
        remove_flag = kwargs['remove'] or False
        if remove_flag:  # Remove marked files only
            print("Removing marked Items...")
            do_mark_for_trash = False
            do_delete = True
        elif delete_flag:
            print("Marking then deleting Item...")
            do_mark_for_trash = True
            do_delete = True
        else:
            print("Marking Items for trash...")
            do_mark_for_trash = True
            do_delete = False

        if do_mark_for_trash:
            # Get all item ids for delivered items
            delivered_items = set()
            for delivery_item in DeliveryItem.objects.all():
                delivered_items.add(delivery_item.item.id)
            print(f"Items in DeliveryItem: {len(delivered_items)}")

            # Get all items with matching cmsid
            matching_cmsitems = set()
            for item in Item.objects.all():
                #print(f"Item #{item.id}; CMSid #{item.cmsid}")
                try:
                    cmsitem = InventoryItem.objects.get(id=item.cmsid)
                except:
                    cmsitem = None
                if cmsitem:
                    print(f"Found CMS item with id #{cmsitem.id}")
                    matching_cmsitems.add(item.id) 
            print(f"Matching cmsItems in Item: {len(matching_cmsitems)}")

            # Combine sets as items to keep
            items_to_keep = delivered_items.union(matching_cmsitems)
            print(f"Total items to keep: {len(items_to_keep)}")
            
            count = 0
            marked_set = set()
            for item in Item.objects.all():
                count += 1
                if item.id not in items_to_keep:
                    print(f"Items for deletion #{item.id:<6}|{item.name}")
                    marked_set.add(item.id)
            print(f"Processed: {count}, marked for delete: {len(marked_set)}")

            if len(marked_set) == 0:
                print("No files to delete")
            elif do_delete:  # Delete
                confirm_delete = input("Are you sure you want to delete the items? Type 'YES' to confirm: ")
                if confirm_delete == 'YES':
                    count = 0
                    for item_id in marked_set:
                        item = Item.objects.get(pk=item_id)
                        print(f"#{item.id:<6}|{item.name}")
                        item.delete()
                        count += 1                    
                self.stdout.write(f"Deleted {count} items")

            else:  # Mark as Trash, no deletion
                count = 0
                marked_set = set()
                for item in Item.objects.all():
                    count += 1
                    if item.id not in items_to_keep:
                        print(f"Mark for deletion #{item.id:<6}|{item.name}")
                        if item.note:
                            item.note = f"Marked for deletion [{timezone.now()}]" + str(item.note)
                        else:
                            item.note = f"Marked for deletion [{timezone.now()}]"
                        item.save()
                        marked_set.add(item.id)
                        
                self.stdout.write(f"Marked {len(marked_set)} items for deletion. Use -r flag to delete marked files")

        elif do_delete:
            marked_set = Item.objects.filter(
                note__icontains="Marked for deletion"
            )
            print(f"Got {marked_set.count()} items marked for deletion")
            count = 0
            for item in marked_set:
                print(f"#{item.id:<6}|{item.name}")
                count += 1     
            confirm_delete = input("Are you sure you want to delete the items? Type 'YES' to confirm: ")
            if confirm_delete == 'YES':
                count = 0
                for item in marked_set:
                    print(f"Deleting #{item.id:<6}|{item.name}")
                    item.delete()
                    count += 1                    
                self.stdout.write(f"Deleted {count} items")
