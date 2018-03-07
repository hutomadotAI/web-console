#!/bin/bash

function check_return_code {
    return_code=$?;
    if [[ $return_code != 0 ]]; then
        exit $return_code;
    fi
}

# If we can't even display the Django version something went badly wrong
echo "Checking Django configuration works"
python manage.py version
check_return_code

# Process statics so we can run further commands
echo "Process statics"
python manage.py collectstatic --noinput
check_return_code

# Check if database is ready
echo "Checking Database"
while ! python manage.py showmigrations 2> /dev/null; do
  echo "Database isn’t ready yet"
  sleep 1
done

# Check API is ready
echo "Checking API"
while ! curl --insecure --silent --connect-timeout 1 $API_URL/health/ping; do
  echo "API isn’t ready yet"
  sleep 1
done

# Run migrations
echo "Running migrations"
python manage.py migrate
check_return_code

# Launch serve app
echo "Starting Django"
gunicorn -b :8000 app.wsgi
