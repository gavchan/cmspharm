"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Get environment to determine Django settings, default to production
if os.getenv('DJ_RUNENV') == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
