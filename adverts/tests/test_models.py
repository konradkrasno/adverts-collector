import os

import pytest
from adverts.models import Plot
from adverts.tests.conftest import TEST_DIR


@pytest.mark.django_db
class TestPlot:
    """ Class for testing Advert's model methods. """

    pytestmark = pytest.mark.django_db

    def test_load_adverts(self, create_test_csv):
        Plot.load_adverts(TEST_DIR)
        assert Plot.objects.exists()

    def test_load_adverts_when_no_files(self):
        try:
            os.remove(os.path.join(os.getcwd(), TEST_DIR, "test_data.csv"))
        except FileNotFoundError:
            pass
        with pytest.raises(FileNotFoundError):
            Plot.load_adverts(TEST_DIR)

    def test_delete_duplicates(self):
        assert len(Plot.objects.all()) == 3

    def test_filter_plots(self):
        assert (
            Plot.manager.filter_plots(
                place="Dębe Wielkie", price=400000, area=800
            ).values("place")[0]["place"]
            == "Dębe Wielkie"
        )

        assert (
            Plot.manager.filter_plots(place="None", price=200000, area=1000).values(
                "place"
            )[0]["place"]
            == "Rysie"
        )

    def test_search_by_description(self):
        adverts = Plot.objects.all()
        assert Plot.manager.search_by_description(adverts, "media przy działce")

    def test_get_places(self):
        assert len(Plot.get_places()) == 2
