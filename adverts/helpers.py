from typing import *

from django.db.models import QuerySet

from .models import Plot


def get_adverts(request, advert_type, user=None) -> QuerySet:
    if advert_type == "plot":
        place = request.GET.get("place")
        price = request.GET.get("price")
        area = request.GET.get("area")
        query = request.GET.get("query")
        adverts = Plot.manager.filter_plots(place, price, area, query, user=user)
        return adverts


class Echo:
    """ Helper class for streaming csv file. """

    @staticmethod
    def write(value):
        return value


def prepare_plot_to_csv(adverts: QuerySet) -> List:
    rows = [
        [
            "Miejscowość",
            "Powiat",
            "Cena",
            "Cena za m2",
            "Powierzchnia",
            "Link",
            "Data dodania",
        ]
    ]
    for adv in adverts:
        row = [
            adv.place,
            adv.county,
            adv.price,
            adv.price_per_m2,
            adv.area,
            adv.link,
            adv.date_added,
        ]
        rows.append(row)
    return rows
