'''
Production settings

To use it, on the server export
DJANGO_SETTINGS_MODULE=bookr.settings.production

'''

import dj_database_url
import os
from .base import *  # noqa ignore=F405


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['django-bookr.herokuapp.com/']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# For Heroku we need to use a database url

DATABASES['default'] = dj_database_url.config(  # noqa ignore=F405
    conn_max_age=600, ssl_require=True)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
