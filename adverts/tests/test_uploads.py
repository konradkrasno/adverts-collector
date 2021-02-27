import glob
import os

import pytest
from adverts import uploads
from adverts.models import Plot
from django.conf import settings
from scrapy.crawler import CrawlerProcess


@pytest.mark.django_db
def test_run_spider(mocker):
    mocker.patch("glob.glob")
    mocker.patch.object(CrawlerProcess, "crawl", return_value=True)
    mocker.patch.object(CrawlerProcess, "start", return_value=True)
    mocker.patch("adverts.uploads.upload_plots")
    process = CrawlerProcess()
    uploads.run_spider()
    glob.glob.assert_called_with(f"{settings.SCRAPED_DATA_CATALOG}/*.csv")
    process.crawl.assert_called()
    process.start.assert_called_once()
    uploads.upload_plots.assert_called_once()


@pytest.mark.django_db
def test_upload_data(mocker):
    mocker.patch("adverts.models.Plot.load_adverts")
    mocker.patch("adverts.models.Plot.delete_duplicates")
    uploads.upload_plots()
    Plot.load_adverts.assert_called_with(
        os.path.join(settings.SCRAPED_DATA_CATALOG, "plots")
    )
    Plot.delete_duplicates.assert_called_once()
