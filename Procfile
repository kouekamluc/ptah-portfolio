web: gunicorn portfolio_site.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 60
release: python manage.py migrate && python manage.py collectstatic --noinput
