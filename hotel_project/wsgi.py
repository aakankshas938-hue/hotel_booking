import os
from django.core.wsgi import get_wsgi_application

# Correct path to your settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')

application = get_wsgi_application()
