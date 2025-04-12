from django.contrib import admin
from .models import QAEntry

# For database verification
# use: python manage.py createsuperuser
#      python manage.py runserver
#
# Visit: http://127.0.0.1:8000/admin/ to view and manage your data.

admin.site.register(QAEntry)


