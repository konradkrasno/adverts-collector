from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("upload_data", views.upload_data, name="upload_data"),
    path("", views.plot_search, name="plot_search"),
    path(
        "<str:place>/<int:price>/<int:area>/<str:query>",
        views.plot_list,
        name="plot_list",
    ),
    path("<int:plot_id>", views.plot_detail, name="plot_detail"),
]
