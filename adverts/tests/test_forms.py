import pytest

from adverts.forms import SearchPlotForm


@pytest.mark.django_db
class TestForms:
    """ Class for testing Django forms. """

    pytestmark = pytest.mark.django_db

    def test_advert_form_when_valid(self):
        form = SearchPlotForm({"place": "Warszawa"})
        assert form.is_valid()

        form = SearchPlotForm({}, place_not_required=True)
        assert form.is_valid()

    def test_advert_form_when_invalid(self):
        form = SearchPlotForm({})
        assert not form.is_valid()
        form = SearchPlotForm({"place": "Warszawa", "price": -100})
        assert not form.is_valid()
