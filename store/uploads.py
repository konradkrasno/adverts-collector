import logging

from adverts_collector.settings import SCRAPED_DATA_CATALOG
from django.db.utils import ProgrammingError

from .models import Plot


def upload_plots():
    try:
        Plot.load_adverts(SCRAPED_DATA_CATALOG)
    except (ProgrammingError, FileNotFoundError) as e:
        logging.error(f"ERROR: {e.__str__()}")
    Plot.delete_duplicates()
