import logging

from django.conf import settings
from django.db.utils import ProgrammingError

from .models import Plot


def upload_plots():
    try:
        Plot.load_adverts(settings.SCRAPED_DATA_CATALOG)
    except (ProgrammingError, FileNotFoundError) as e:
        logging.error(f"ERROR: {e.__str__()}")
    Plot.delete_duplicates()
