from config.settings.common import *
import yaml

print("Using production settings")

# Read secret key from a file
with open('dj_secret.key') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Read settings from yaml file
with open('db_settings_prod.yml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    default_db = data['default'][0]
    cms_db = data['cms_db'][0]
    hostname = data['allowed_hosts']

ALLOWED_HOSTS = [hostname]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_ROUTERS = ['db_routers.cms.CmsDbRouter', ]
DATABASE_APPS_MAPPING = {
    'cmsacc': 'cms_db',
    'cmsinv': 'cms_db',
    'cmssys': 'cms_db',
    'drugdb': 'default',
   }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': default_db['name'],
        'USER': default_db['user'],
        'PASSWORD': default_db['password'],
        'HOST': default_db['host'],
        'PORT': default_db['port'],
    },
    'cms_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': cms_db['name'],
        'USER': cms_db['user'],
        'PASSWORD': cms_db['password'],
        'HOST': cms_db['host'],
        'PORT': cms_db['port'],
    },
}

# Misc security settings
SECURE_HSTS_SECONDS = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
