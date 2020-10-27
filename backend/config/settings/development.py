from config.settings.common import *
import yaml

print("Using development settings")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

NOTEBOOK_ARGUMENTS = [
    '--ip=0.0.0.0',
    '--port=8888',
    '--no-browser',
    '--allow-root',
]
# Read secret key from a file
with open('dj_secret.key') as f:
    SECRET_KEY = f.read().strip()

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# Read settings from yaml file
with open('db_settings_dev.yml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    default_db = data['default'][0]
    cms_db = data['cms_db'][0]

# Read postgres password from a file
# with open('pg_settings.env') as f:
#     POSTGRES_PASS = f.read().strip().split("=")[1]

# with open('cms.key') as f:
#     CMS_PASS = f.read().strip()

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
