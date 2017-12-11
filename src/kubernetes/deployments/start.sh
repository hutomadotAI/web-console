#!/bin/bash

function check_return_code {
    return_code=$?;
    if [[ $return_code != 0 ]]; then
        exit $return_code;
    fi
}

# Run migrations
python manage.py migrate
check_return_code

# Ensure super-user exists
python manage.py ensure_hu_superuser --username=superuser --email=admin@hutoma.ai --no-input
check_return_code

# Migrate legacy users
python manage.py migrate_legacy_users
check_return_code

# Process statics
python manage.py collectstatic --noinput
check_return_code

# Launch gunicorn to serve app
gunicorn -b :8000 app.wsgi
