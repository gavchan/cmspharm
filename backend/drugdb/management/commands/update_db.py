import csv, os, sys
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug, Company, Ingredient
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
        company = {
            'name': company_name,
            'address': company_addr,
            'is_active': True,
            'date_created': update_date,
            'last_updated': update_date,
        }
        # company_id, created = Company.objects.get_or_create(name=company_name, defaults=company)
        company_id, created = Company.objects.update_or_create(name=company_name, defaults=company)
        if created:
            self.stdout.write(f"\nAdded: {company_id} | {company_name}")

        
        # Parse product columns
        product = {
            'name': drug_name,
            'reg_no': drug_permit_no,
            'company': company_id,
            # 'tags': tags,
            'is_active': True,
            'date_created': update_date,
            'last_updated': update_date,
        }
        # product_id, created = Product.objects.update_or_create(reg_no=drug_permit_no, defaults=product)
        product_id, created = RegisteredDrug.objects.get_or_create(reg_no=drug_permit_no, defaults=product)
        if created:
            self.stdout.write(f"\nAdded: {product_id} | {drug_permit_no} | {drug_name}")

        # Parse active ingredients
        ingr_list = active_ingredients.split(",")
        for ingredient in ingr_list:
            ingr = ingredient.strip()
            ingredient_id, created = Ingredient.objects.get_or_create(name=ingr)
            ingredient_id.registereddrugs.add(product_id)
            if created:
                self.stdout.write(f"\nAdded: {ingr} from {drug_name}")

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
