"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Get environment to determine Django settings, default to production
if os.getenv('DJ_RUNENV') == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
