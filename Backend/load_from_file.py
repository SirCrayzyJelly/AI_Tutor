import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

try:
    call_command('loaddata', 'initial_data.json')
    print("Podaci su uspješno učitani.")
except Exception as e:
    print(f"Greška pri učitavanju podataka: {e}")
