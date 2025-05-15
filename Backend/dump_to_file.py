import os
import django
from django.core.management import call_command

# Postavi put do Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Dump u JSON fajl s utf-8 encodingom
with open('initial_data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', format='json', indent=2, stdout=f)
