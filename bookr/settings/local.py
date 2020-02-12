'''
Settings for local development

To use it start server with:
python manage.py runserver --settings=bookr.settings.local

'''

from .base import *  # noqa ignore=F405

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=e_1_t=4t&m4^q+vgf87faef314ta88^aj7l9bb8_qfk)q7(9_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bookr',
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
