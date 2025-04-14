import csv
import os
from django.core.management.base import BaseCommand
from chatbot.models import QAEntry

class Command(BaseCommand):
    help = 'Imports QA pairs from a CSV file into the Message model'

    def add_arguments(self, parser):
        # Add a positional argument for the CSV file path
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        # Get the file path from the arguments
        csv_file = kwargs['csv_file']

        # Check if the file exists
        if not os.path.isfile(csv_file):
            self.stdout.write(self.style.ERROR(f"The file {csv_file} does not exist"))
            return

        # Open the CSV file and read its contents
        try:
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                for row in reader:
                    # Skip empty rows or rows with less than 3 elements
                    if len(row) < 3:
                        continue

                    # Extract data
                    lecture_id = int(row[0])  # Assuming lecture_id is an integer
                    question = row[1]
                    answer = row[2]
                    link = row[3].strip() if len(row) > 3 and row[3].strip() else None

                    # Create a new QAEntry in the database
                    QAEntry.objects.create(
                        lecture_id=lecture_id,
                        question=question,
                        answer=answer,
                        link=link
                    )

            self.stdout.write(self.style.SUCCESS('CSV file has been imported successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))