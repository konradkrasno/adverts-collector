import glob
import logging
import os

from adverts_crawler.adverts_crawler.spiders.scraper import (
    MorizonSpider,
    AdresowoSpider,
    StrzelczykSpider,
)
from celery import shared_task
from django.conf import settings
from django.db.utils import ProgrammingError
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .models import Plot


@shared_task
def upload_plots():
    try:
        Plot.load_adverts(os.path.join(settings.SCRAPED_DATA_CATALOG, "plots"))
    except (ProgrammingError, FileNotFoundError) as e:
        logging.error(f"ERROR: {e.__str__()}")
    Plot.delete_duplicates()
    logging.info("Data successfully updated.")


@shared_task
def run_spider() -> None:
    # remove files
    [os.remove(file) for file in glob.glob(f"{settings.SCRAPED_DATA_CATALOG}/*.csv")]

    # crawl data
    s = get_project_settings()
    s["FEED_FORMAT"] = "csv"
    s["FEED_URI"] = f"{settings.SCRAPED_DATA_CATALOG}/plots/plots.csv"
    process = CrawlerProcess(s)
    process.crawl(MorizonSpider)
    process.crawl(AdresowoSpider)
    process.crawl(StrzelczykSpider)
    process.start()
    logging.info("Data scraped successfully")

    # Upload data to db
    upload_plots()
