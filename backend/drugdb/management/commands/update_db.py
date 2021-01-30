import csv, os, sys
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug, Company, Ingredient
from inventory.models import Item
from django.conf import settings
from django.utils import timezone
import pytz

class Command(BaseCommand):
    """
    Imports scraped drug list and parses data into respective models
    """
    help = 'Import .csv drug database file'

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def update_or_create(self, line, update_date):
        """
        Takes line and splits items in the list into product and company objects,
        then updates or creates records in the list
        """
        # self.stdout.write(f"Writing to database: {line[1]} | {line[3]}")
        sys.stdout.write(".")
        sys.stdout.flush()
        drug_name = line[0]
        drug_permit_no = line[1]
        active_ingredients = line[2]
        company_name = line[3]
        company_addr = line[4]
        if len(line) < 6:
            # Tag column is blank
            tags = ""
        else:
            tags = line[5]

        # Parse company columns
        company_data = {
            'name': company_name,
            'address': company_addr,
            'is_active': True,
            'date_created': update_date,
            'last_updated': update_date,
        }
        # company, created = Company.objects.get_or_create(name=company_name, defaults=company_data)
        company, created = Company.objects.update_or_create(name=company_name, defaults=company_data)
        if created:
            self.stdout.write(f"\nAdded: {company.id} | {company.name}")

        # Try match item
        try:
            matched_item = Item.objects.get(reg_no=drug_permit_no)
        except:
            matched_item = None
        # Parse product columns
        product = {
            'name': drug_name,
            'reg_no': drug_permit_no,
            'company': company,
            'item': matched_item,
            # 'tags': tags,
            'is_active': True,
            'date_created': update_date,
            'last_updated': update_date,
            'last_synced': update_date,
        }
        # regdrug, created = Product.objects.update_or_create(reg_no=drug_permit_no, defaults=product)
        regdrug, created = RegisteredDrug.objects.get_or_create(reg_no=drug_permit_no, defaults=product)
        if created:
            self.stdout.write(f"\nAdded: {regdrug.id} | {drug_permit_no} | {drug_name}")
            if matched_item:
                self.stdout.write(f"\nMatched item #{matched_item.id} with {drug_permit_no}")

            # Parse active ingredients
            ingr_list = active_ingredients.split(",")
            for ingredient in ingr_list:
                ingr = ingredient.strip()
                ingredient_obj, created = Ingredient.objects.get_or_create(name=ingr)
                ingredient_obj.registereddrugs.add(regdrug)
                if created:
                    self.stdout.write(f"\nAdded: {ingr} from {drug_name}")
        elif regdrug:  # Update regdrug.last_synced
            old_item = regdrug.item
            regdrug.last_synced = update_date
            if matched_item:
                if old_item != matched_item:
                    # Update regdrug item
                    self.stdout.write(f"\nMatched {regdrug.reg_no} - {regdrug.name} with Item #{match_item.id} - {matched_item.name}")
                    self.stdout.write(f"\n! Update item #{old_item} to #{matched_item.id}")
                    regdrug.item = matched_item
            regdrug.save()

    def inactivate_drug(self, drug, update_date):
        registeredDrug = drug
        drug.is_active = False
        last_updated = update_date
        drug.save()
        self.stdout.write(f"{drug.reg_no} | {drug.name} set inactive\n")
        return

    def handle(self, *args, **options):
        DRUGS_CSV_FILE = options['csvfile']
        filepath = os.path.join(settings.BASE_DIR, DRUGS_CSV_FILE)
        self.stdout.write('Updating drug list from {}'.format(filepath))

        # Try parse date from final 8 characters (YYYYMMDD)
        db_date_str = DRUGS_CSV_FILE.split('.')[0][-8:]
        print(db_date_str)
        try:
            db_date = timezone.make_aware(datetime.strptime(db_date_str, '%Y%m%d'))
        except:
            print('No valid date, using today\'s date')
            db_date = timezone.now()
        print(db_date.strftime('%Y-%m-%d'))
        lines = []
        active_permits = []
        try:
            with open(filepath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='|')
                row = 0
                for line in csv_reader:
                    if row == 0:
                        # Skip header row
                        pass
                    else:
                        lines.append(line)
                        self.stdout.write('[{}] {}'.format(
                            row-1, '|'.join(line)
                        ))
                    row += 1
        except:
            self.stdout.write('Error reading .csv file')            
            return -1
        self.stdout.write(f"Number of records: {len(lines)}")
        self.stdout.write("====\nWriting to database:\n=====\n")
        for line in lines:
            self.update_or_create(line, db_date)
            active_permits.append(line[1])

        # Loop through drug records and check if permit_no no longer exists
        # If permit_no no longer exists, to set as inactive.
        self.stdout.write("====\nChecking for expired permits\n=====\n")
        print(active_permits)

        inactive_drugs = RegisteredDrug.objects.exclude(reg_no__in=active_permits)
        for drug in inactive_drugs:
            self.inactivate_drug(drug, db_date)
