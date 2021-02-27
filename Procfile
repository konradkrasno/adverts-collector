web: python manage.py makemigrations account errors adverts; python manage.py migrate; gunicorn adverts_collector.wsgi
worker: celery -A adverts_collector worker -l info
beat: celery -A adverts_collector beat -l info
