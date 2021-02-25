from django.urls import path
from . import views

app_name = "adverts"

urlpatterns = [
    path("upload_data", views.upload_data, name="upload_data"),
    path("", views.plot_search, name="plot_search"),
    path("<int:plot_id>", views.plot_detail, name="plot_detail"),
]
