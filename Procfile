release: python manage.py migrate --settings=bookr.settings.production
web: gunicorn bookr.wsgi --log-file -
