import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from drugdb.models import RegisteredDrug, Company, Ingredient
from cmsinv.models import (
    InventoryItem, Prescription, PrescriptionDetail, InventoryMovementLog,
    DepletionItem, ReceivedItem
)
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    """
    Cleans CMS InventoryItem database - mark unused items for Trash
    """
    help = 'Cleans CMS InventoryItem database - mark unused items for Trash'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--delete', action='store_true', help='Mark and delete')
        parser.add_argument('-f', '--force', action='store_true', help='Force delete (No prompt)')
        parser.add_argument('-r', '--remove', action='store_true', help='Remove marked/trashed')
        
    def handle(self, *args, **kwargs):
        delete_flag = kwargs['delete'] or False
        remove_flag = kwargs['remove'] or False
        force_flag = kwargs['force'] or False
        if remove_flag:  # Remove marked files only
            print("Removing marked files...")
            do_mark_for_trash = False
            do_delete = True
        elif delete_flag:
            print("Marking then deleting files...")
            do_mark_for_trash = True
            do_delete = True
        else:
            print("Marking files for trash...")
            do_mark_for_trash = True
            do_delete = False

        if do_mark_for_trash:
            # Get all Prescribed drug ids
            prescribed_set = set()
            for record in PrescriptionDetail.objects.all():
                prescribed_set.add(record.drug.id)
            print(f"Prescribed count: {len(prescribed_set)}")

            # Get all Received drug ids
            received_set = set()
            for received in ReceivedItem.objects.all():
                received_set.add(received.drug_item_id)
            print(f"Received count: {len(received_set)}")

            # Get all Depleted drug ids
            depleted_set = set()
            for depleted_item in DepletionItem.objects.all():
                depleted_set.add(depleted_item.drug_id)
            print(f"Depleted count: {len(depleted_set)}")

            # Check 
            # Combine sets as utilized items
            utilized_set = prescribed_set.union(received_set).union(depleted_set)
            print(f"Total utilized count: {len(utilized_set)}")
            
            # Mark empty items
            mark_for_delete = InventoryItem.objects.filter(
                stock_qty=0,
                last_updated__isnull=True,
                clinic_drug_no__isnull=True,
            ).filter(
                Q(updated_by__isnull=True) |
                Q(updated_by__exact='')
            )
            marked_set = set()
            for item in mark_for_delete:
                marked_set.add(item.id)
            print(f"Marked for delete count: {len(marked_set)}")

            # Exclude utilized set from marked set
            final_set = marked_set.difference(utilized_set)
            print(f"Final (marked - utilized) set count: {len(final_set)}")
            intersect = marked_set.intersection(utilized_set)
            for item in intersect:
                if item in final_set:
                    print(f'-- Error: Unexpected item #{item} marked for delete')
                else:
                    print(f'-- Item #{item} excluded from final deletion')

            if len(final_set) == 0:
                print("No files to delete")
            elif do_delete:  # Delete
                if force_flag:
                    confirm_delete = 'YES'
                else:
                    confirm_delete = input("Are you sure you want to delete the items? Type 'YES' to confirm: ")
                
                if confirm_delete == 'YES':
                    count = 0
                    for item_id in final_set:
                        item = InventoryItem.objects.get(pk=item_id)
                        print(f"#{item.id:<6}|{item.discontinue}|{item.product_name}")
                        item.delete()
                        count += 1                    
                self.stdout.write(f"Deleted {count} items")

            else:  # Mark as Trash, no deletion
                count = 0
                for item_id in final_set:
                    item = InventoryItem.objects.get(pk=item_id)
                    print(f"#{item.id:<6}|{item.discontinue}|{item.product_name}")
                    item.location = "Trash"
                    item.remarks = "Marked for deletion [{timezone.now()}]"
                    item.save()
                    count += 1
                self.stdout.write(f"Marked {count} items for deletion. Use -r flag to delete marked files")

        elif do_delete:
            final_set = InventoryItem.objects.get(
                location="Trash",
                remarks__icontains="Marked for deletion"
            )
            print(f"Got {final_set.count()} items marked for deletion")
            confirm_delete = input("Are you sure you want to delete the items? Type 'YES' to confirm: ")
            if confirm_delete == 'YES':
                count = 0
                for item in final_set:
                    print(f"#{item.id:<6}|{item.discontinue}|{item.product_name}")
                    item.delete()
                    count += 1
                self.stdout.write(f"Deleted {count} items")
