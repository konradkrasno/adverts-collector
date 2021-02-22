import glob
import logging
import os
from typing import *

import pandas as pd
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models, transaction
from django.db.utils import ProgrammingError
from django.urls import reverse


class PlotManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super(PlotManager, self).get_queryset()

    def filter_plots(
        self, place: str = None, price: int = None, area: int = None, query: str = None
    ) -> models.QuerySet:
        """ Returns objects filtered by place, maximum price and minimum area ordered by price. """

        plots = self.get_queryset()
        if place and place != "None":
            plots = plots.filter(place=place).order_by("price")
        if price and price != 0 and price != "None":
            plots = plots.filter(price__lte=price).order_by("price")
        if area and area != 0 and area != "None":
            plots = plots.filter(area__gte=area).order_by("price")
        plots = self.search_by_description(plots, query)
        return plots

    @staticmethod
    def search_by_description(
        objects: models.QuerySet, search_text: str
    ) -> models.QuerySet:
        if search_text and search_text != "None":
            vector = SearchVector("description")
            query = SearchQuery(search_text)
            objects = (
                objects.annotate(search=vector, rank=SearchRank(vector, query))
                .filter(search=search_text)
                .order_by("-rank")
            )
        return objects


class Plot(models.Model):
    """ Stores scraped building plots data. """

    place = models.CharField(max_length=100, null=True)
    county = models.CharField(max_length=100, null=True)
    price = models.FloatField(null=True)
    price_per_m2 = models.FloatField(null=True)
    area = models.FloatField(null=True)
    link = models.CharField(max_length=500, null=True)
    date_added = models.CharField(max_length=25, null=True)
    description = models.TextField(null=True)
    image_url = models.CharField(max_length=500, null=True)
    objects = models.Manager()
    manager = PlotManager()

    class Meta:
        ordering = ("price",)

    def __str__(self):
        return self.place

    def get_absolute_url(self):
        return reverse("store:plot_detail", args=[self.id])

    @classmethod
    def create_from_csv(cls, item: list) -> None:
        """ Creates an Advert instance. """
        try:
            with transaction.atomic():
                cls(
                    place=item[0],
                    county=item[1],
                    price=item[2],
                    price_per_m2=item[3],
                    area=item[4],
                    link=item[5],
                    date_added=item[6],
                    description=item[7],
                    image_url=item[8],
                ).save()
        except ValueError as e:
            logging.error(e)

    @classmethod
    def load_adverts(cls, catalog: str) -> None:
        """
        Loads data from files and saves to the database.

        :param catalog: Catalog name with files to be added.
        """

        path = os.path.join(catalog, "*.csv")
        files = glob.glob(path)

        if files:
            for file in files:
                adv = pd.read_csv(file)
                try:
                    for item in adv.values:
                        cls.create_from_csv(item)
                except ProgrammingError:
                    raise ProgrammingError(
                        "You have to make migrations before add data to database."
                    )
        else:
            raise FileNotFoundError("No files to added.")
        logging.info("Data successfully updated.")

    @classmethod
    def delete_duplicates(cls) -> None:
        """ Deletes duplicate objects from the database. """

        min_id_objects = cls.objects.values(
            "place", "price", "price_per_m2", "area"
        ).annotate(minid=models.Min("id"))
        min_ids = [obj["minid"] for obj in min_id_objects]

        cls.objects.exclude(id__in=min_ids).delete()

        logging.info(
            "Amount of adverts after deleting duplicates: {}".format(
                len(cls.objects.all())
            )
        )

    @classmethod
    def get_places(cls) -> Tuple:
        return tuple(
            set(
                cls.objects.only("place")
                .values_list("place", flat=True)
                .order_by("place")
            )
        )


class SavedAdverts(models.Model):
    """ Creates relationships between the user and its saved adverts.  """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="saved_adverts"
    )
    plots = models.ManyToManyField(Plot)
