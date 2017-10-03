#!/bin/bash

# Proceed statics
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --fake-initial
# python manage.py loaddata initial_data

# Launch gunicorn to serve app
gunicorn -b :8000 app.wsgi
