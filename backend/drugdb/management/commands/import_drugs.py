import csv, os
from django.core.management.base import BaseCommand, CommandError
from drugdb.models import RegisteredDrug, Company
from django.conf import settings

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

    def update_or_create(self, line):
        """
        Takes line and splits items in the list into registered_drug and company objects,
        then updates or creates records in the list
        """
        self.stdout.write(f"Writing to database: {line[1]} | {line[3]}")
        
        drug_name = line[0]
        drug_permit_no = line[1]
        active_ingredients = line[2]
        company_name = line[3]
        company_addr = line[4]

        company = {
            'name': company_name,
            'address': company_addr,
        }
        company_id, created = Company.objects.update_or_create(name=company_name, address=company_addr, defaults=company)
        registered_drug = {
            'name': drug_name,
            'permit_no': drug_permit_no,
            'ingredients': active_ingredients,
            'company': company_id
        }
        RegisteredDrug.objects.update_or_create(permit_no=drug_permit_no, defaults=registered_drug)


    def handle(self, *args, **options):
        DRUGS_CSV_FILE = options['csvfile']
        filepath = os.path.join(settings.BASE_DIR, DRUGS_CSV_FILE)
        self.stdout.write('Importing drug list from {}'.format(filepath))

        lines = []
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
        self.stdout.write(f"Records: {len(lines)}")
        self.stdout.write(f"1st: {lines[0]}")
        self.stdout.write(f"Last: {lines[-1]}")
        self.stdout.write("====\nAdding to database")
        for line in lines:
            self.update_or_create(line)
        