from django.core.management.base import BaseCommand
from chatbot.models import QAEntry, Subject
import csv
import os

class Command(BaseCommand):  # <== This is crucial!
    help = 'Imports QA pairs from a CSV file into the QAEntry model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('--subject', type=str, required=True, help='Name of the subject')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        subject_name = options['subject']

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        subject, _ = Subject.objects.get_or_create(name=subject_name)

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if len(row) < 3:
                    continue
                lecture_id = int(row[0])
                question = row[1]
                answer = row[2]
                link = row[3].strip() if len(row) > 3 and row[3].strip() else None

                QAEntry.objects.create(
                    lecture_id=lecture_id,
                    subject=subject,
                    question=question,
                    answer=answer,
                    link=link
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully imported QA entries for subject "{subject_name}".'))
