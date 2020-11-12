import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug, Company, Ingredient
from cmsinv.models import InventoryItem, Supplier
from django.conf import settings

class Command(BaseCommand):
    """
    Match registered drug list for product/label/generic/ingredients list
    """
    help = 'Match registered drug list for product/label/generic/ingredients list'

    def handle(self, *args, **options):

        # Loop through CMS inventory item records, match registered drugs with same reg_no
        items = InventoryItem.objects.all()

        item_count = 0
        updated_count = 0

        for item in items:
            item_count += 1

            # Check for matching Registered drug based on reg_no
            try:
                drug_obj = RegisteredDrug.objects.get(reg_no=item.registration_no) or None
            except RegisteredDrug.DoesNotExist:
                self.stdout.write(f"\n#{item.id:4} | Skip [{item.registration_no}] {item.product_name} - No matching Reg Drug.")
                continue
            if drug_obj:
                updated_count += 1
                
                old_product_name = item.product_name
                old_label_name = item.label_name
                old_generic_name = item.generic_name
                # If alias is None, set as old_product_name

                if item.alias is None:
                    item.alias = old_product_name
                item.product_name = drug_obj.name
                item.label_name = drug_obj.name
                item.ingredient = drug_obj.ingredients_list
                # item.generic_name = ' '.join([drug_obj.gen_generic, drug_obj.gen_dosage]).strip()
                # Above commented version tags on generated dosage to generic_name
                item.generic_name = drug_obj.gen_generic.strip()
                
                self.stdout.write(f"#{item.id:4} | PRODUCT [{old_product_name}] => [{item.product_name}]")
                self.stdout.write(f"#{item.id:4} | LABEL   [{old_label_name}] => [{item.label_name}]")
                self.stdout.write(f"#{item.id:4} | GENERIC [{old_generic_name}] => [{item.generic_name}]")
                self.stdout.write(f"#{item.id:4} | INGR => [{item.ingredient}]=====")

                item.save()
            # drug_count += 1
            # active_ingr = drug.ingredient_list.split(',')
            # for ingredient in active_ingr:
            #     ingr = ingredient.strip()
            #     ingredient_id, created = Ingredient.objects.get_or_create(name=ingr)
            #     ingredient_id.registereddrugs.add(drug.id)
            #     if created:
            #         self.stdout.write(f"Added {ingr} from {drug.name}")
            #         ingr_count += 1

        self.stdout.write(f"\n==== Done ====\nParsed {item_count} drugs; updated {updated_count} ingredients")
