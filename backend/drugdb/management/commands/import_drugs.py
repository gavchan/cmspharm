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
        # try:
        #     with open(DRUGS_CSV_FILE, 'r') as csv_file:
        #         csv_reader = csv.reader(csv_file, delimiter='|')
        #         i = 0
        #         for line in csv_reader:
        #             # self.stdout.write(line)
        #             self.stdout.write(i)
        #             i+=1
        # except:
        #     self.stdout.write('Error reading .csv file')
        #     return -1

        