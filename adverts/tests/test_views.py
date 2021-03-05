import pytest
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse

from adverts import tasks
from adverts import uploads
from adverts import views
from adverts.models import Plot


@pytest.mark.django_db
class TestViews:
    """ Class for testing Django Views. """

    pytestmark = pytest.mark.django_db

    def test_run_spider(self, client, mocker):
        mocker.patch("adverts.uploads.run_spider.delay")
        response = client.get(reverse("adverts:crawl_data"))
        assert response.status_code == 200
        uploads.run_spider.delay.assert_called_once()

    def test_upload_data(self, client, mocker):
        mocker.patch("adverts.uploads.upload_plots.delay")
        response = client.get(reverse("adverts:upload_data"))
        assert response.status_code == 200
        uploads.upload_plots.delay.assert_called_once()

    def test_plot_search(self, client):
        kwargs = {
            "place": "Dębe Wielkie",
            "price": 400000,
            "area": 800,
        }
        response = client.get(reverse("adverts:plot_search"), data=kwargs)
        assert response.status_code == 200
        assert (
            response.request.get("QUERY_STRING")
            == "place=D%C4%99be+Wielkie&price=400000&area=800"
        )
        assert len(response.context.get("plots").object_list) == 1

    def test_plot_detail(self, client):
        plot = Plot.objects.first()
        response = client.get(reverse("adverts:plot_detail", kwargs={"plot_id": plot.id}))
        assert response.status_code == 200
        assert response.context.get("plot") == Plot.objects.get(id=plot.id)

    def test_saved_plots_list(self, user, client, save_plots):
        kwargs = {
            "place": "Dębe Wielkie",
            "price": 400000,
            "area": 800,
        }
        response = client.get(reverse("adverts:saved_plots"), data=kwargs)
        assert response.status_code == 200
        assert (
            response.request.get("QUERY_STRING")
            == "place=D%C4%99be+Wielkie&price=400000&area=800"
        )
        assert len(response.context.get("plots").object_list) == 1
    
    def test_advert_save_when_bad_request(self, user, client):
        response = client.post(reverse("adverts:save"))
        assert response.status_code == 400

    def test_advert_save_when_advert_not_exists(self, user, client):
        response = client.post(reverse("adverts:save"), {"id": '1000', "type": "plot", "action": "save"}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        assert response.status_code == 200
        assert not user.saved_plots.all()
    
    def test_advert_save_when_save(self, user, client):
        plot = Plot.objects.first()
        response = client.post(reverse("adverts:save"), {"id": plot.id, "type": "plot", "action": "save"}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        assert response.status_code == 200
        assert user.saved_plots.first() == plot

    def test_advert_save_when_delete(self, user, client, save_plots):
        plot = user.saved_plots.first()
        response = client.post(reverse("adverts:save"), {"id": plot.id, "type": "plot", "action": "remove"}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        assert response.status_code == 200
        assert plot not in user.saved_plots.all()

    def test_save_all_adverts(self, user, client):
        response = client.post(
            reverse("adverts:save_all_adverts", kwargs={"advert_type": "plot"}),
            HTTP_REFERER="http://foo/bar",
        )
        assert response.status_code == 302
        assert len(user.saved_plots.all()) == 3

    def test_delete_all_adverts(self, user, client, save_plots):
        response = client.post(
            reverse(
                "adverts:delete_all_adverts",
                kwargs={"advert_type": "plot", "section": None},
            ),
            HTTP_REFERER="http://foo/bar",
        )
        assert response.status_code == 302
        assert list(user.saved_plots.all()) == []

    def test_download_csv(self, client, save_plots):
        response = client.post(
            reverse(
                "adverts:download_csv", kwargs={"advert_type": "plot", "section": None}
            )
        )
        assert response.status_code == 200
        assert (
            response.get("Content-Disposition")
            == '''attachment; filename="your_adverts.csv"'''
        )

    def test_send_csv(self, user, client, save_plots, mocker):
        mocker.patch("adverts.tasks.send_email.delay")
        response = client.post(
            reverse(
                "adverts:send_csv", kwargs={"advert_type": "plot", "section": None}
            ),
            HTTP_REFERER="http://foo/bar",
        )
        assert response.status_code == 302
        tasks.send_email.delay.assert_called_once()
