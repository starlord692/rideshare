import os
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rideshare_backend.settings')

# This allows us to run standard django setup without the command line
import django
django.setup()
