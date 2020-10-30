import csv, os, sys
from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug, Company, Ingredient
from django.conf import settings

class Command(BaseCommand):
    """
    Convert existing ingredient_list into respective Ingredient model
    """
    help = 'Parses existing ingredient_list into respective Ingredient model'

    def handle(self, *args, **options):

        # Loop through drug records and parse ingredient_list
        drugs = RegisteredDrug.objects.all()

        drug_count = 0
        ingr_count = 0
        for drug in drugs:
            drug_count += 1
            active_ingr = drug.ingredient_list.split(',')
            for ingredient in active_ingr:
                ingr = ingredient.strip()
                ingredient_id, created = Ingredient.objects.get_or_create(name=ingr)
                ingredient_id.registereddrugs.add(drug.id)
                if created:
                    self.stdout.write(f"Added {ingr} from {drug.name}")
                    ingr_count += 1

        self.stdout.write(f"\n==== Done ====\nParsed {drug_count} drugs; added {ingr_count} ingredients")
