import sys
import os
import django
import pytest

# dodavanje root-a projekta u PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# postavljanje django postavki
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")

django.setup()
