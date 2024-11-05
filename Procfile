web: gunicorn contactsproject.wsgi
worker: celery -A contactsproject worker --loglevel=info
beat: celery -A contactsproject beat --loglevel=info