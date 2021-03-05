from django.urls import path

from . import views

app_name = "adverts"

urlpatterns = [
    path("crawl_data/", views.crawl_data, name="crawl_data"),
    path("upload_data/", views.upload_data, name="upload_data"),
    path("plots/", views.plot_search, name="plot_search"),
    path("plot/<int:plot_id>/", views.plot_detail, name="plot_detail"),
    path("saved/", views.saved_adverts, name="saved_adverts"),
    path("saved/plots/", views.saved_plots_list, name="saved_plots"),
    path(
        "save/", views.advert_save, name="save"
    ),
    path(
        "save_all/<str:advert_type>/", views.save_all_adverts, name="save_all_adverts"
    ),
    path(
        "delete_all/<str:advert_type>/<str:section>/",
        views.delete_all_adverts,
        name="delete_all_adverts",
    ),
    path(
        "download_csv/<str:advert_type>/<str:section>",
        views.download_csv,
        name="download_csv",
    ),
    path(
        "send_csv/<str:advert_type>/<str:section>",
        views.sending_csv,
        name="send_csv",
    ),
]
