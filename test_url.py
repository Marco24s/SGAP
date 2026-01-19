import os
import django
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGAP.settings')
django.setup()

try:
    print("Attempting to import finance.api_views...")
    from finance import api_views
    print("Import SUCCESS")
    
    print("Attempting to reverse URL...")
    url = reverse('finance:api_create_program')
    print(f"URL Resolved: {url}")
except Exception as e:
    print(f"ERROR: {e}")
