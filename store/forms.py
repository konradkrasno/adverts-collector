from django import forms

from .fields import ListTextWidget
from .validators import validate_positive


class SearchPlotForm(forms.Form):
    place = forms.CharField(
        max_length=250,
        label="Miejscowość",
        help_text="Podaj lokalizację działki - pole wymagane",
        required=True,
    )
    price = forms.IntegerField(
        label="Cena",
        help_text="Podaj maksymalną cenę - pole opcjonalne",
        required=False,
        validators=[validate_positive],
    )
    area = forms.IntegerField(
        label="Powierzchnia",
        help_text="Podaj minimalną powierzchnię w metrach kwadratowych - pole opcjonalne",
        required=False,
        validators=[validate_positive],
    )
    query = forms.CharField(
        label="Wyszukaj w opisie",
        help_text="Wpisz frazę, którą chcesz wyszukać w opisie - pole opcjonalne",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        _data_list = kwargs.pop("data_list", None)
        super().__init__(*args, **kwargs)
        self.fields["place"].widget = ListTextWidget(
            data_list=_data_list, name="place-list"
        )

    def clean(self):
        data = super().clean()
        for key, val in data.items():
            if val == "":
                data[key] = "None"
            elif val is None:
                data[key] = 0
        return data
