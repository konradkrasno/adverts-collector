import os
from pathlib import Path

from dotenv import load_dotenv

from celery import Celery

# Load config variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.joinpath(".env"))

# set the default Django settings module for the 'celery' program.
if os.environ.get("DEBUG") is not None:
    settings_module = "adverts_collector.prod_settings"
else:
    settings_module = "adverts_collector.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

app = Celery("adverts_collector")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
