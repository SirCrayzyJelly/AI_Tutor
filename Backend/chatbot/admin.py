from django.contrib import admin
from .models import QAEntry

# For database verification
# use: python manage.py createsuperuser
#      python manage.py runserver
#

admin.site.register(QAEntry)


