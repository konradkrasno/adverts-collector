import csv
from io import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse

from . import tasks
from . import uploads
from .forms import SearchPlotForm
from .helpers import get_adverts, Echo, prepare_plot_to_csv
from .models import Plot
from .pagination import paginate


def crawl_data(request):
    uploads.run_spider.delay()
    return JsonResponse({"OK": "Crawling data started."})


def upload_data(request):
    uploads.upload_plots.delay()
    return JsonResponse({"OK": "Uploading data started."})


def plot_search(request):
    plots = []
    place = request.GET.get("place")
    price = request.GET.get("price")
    area = request.GET.get("area")
    query = request.GET.get("query")
    page = request.GET.get("page")
    form = SearchPlotForm(data_list=Plot.get_places())
    if place:
        form = SearchPlotForm(request.GET, data_list=Plot.get_places())
        if form.is_valid():
            data = form.cleaned_data
            place = data.get("place")
            price = data.get("price")
            area = data.get("area")
            query = data.get("query")
        object_list = Plot.manager.filter_plots(place, price, area, query)
        plots = paginate(object_list, page, 6)
    return render(
        request,
        "adverts/plot/search.html",
        {
            "form": form,
            "place": place,
            "price": price,
            "area": area,
            "query": query,
            "page": page,
            "plots": plots,
            "section": "search",
        },
    )


def plot_detail(request, plot_id: int):
    plot = get_object_or_404(Plot, id=plot_id)
    return render(request, "adverts/plot/detail.html", {"plot": plot})


@login_required
def saved_adverts(request):
    return render(request, "adverts/adverts/saved.html")


@login_required
def saved_plots_list(request):
    place = request.GET.get("place")
    price = request.GET.get("price")
    area = request.GET.get("area")
    query = request.GET.get("query")
    page = request.GET.get("page")
    form = SearchPlotForm(
        request.GET,
        data_list=Plot.get_places(request.user.saved_plots),
        place_not_required=True,
    )
    if form.is_valid():
        data = form.cleaned_data
        place = data.get("place")
        price = data.get("price")
        area = data.get("area")
        query = data.get("query")
    object_list = Plot.manager.filter_plots(
        place, price, area, query, user=request.user
    )
    plots = paginate(object_list, page, 6)
    return render(
        request,
        "adverts/plot/saved.html",
        {
            "form": form,
            "place": place,
            "price": price,
            "area": area,
            "query": query,
            "page": page,
            "plots": plots,
            "section": "saved",
        },
    )


@login_required
def save_advert(request, advert_type: str, advert_id: int):
    if advert_type == "plot":
        plot = get_object_or_404(Plot, id=advert_id)
        request.user.saved_plots.add(plot)
        request.user.save()
        messages.success(request, "Pomyślnie zapisano ogłoszenie.")
    return redirect(request.META["HTTP_REFERER"])


@login_required
def delete_advert(request, advert_type: str, advert_id: int):
    if advert_type == "plot":
        plot = get_object_or_404(Plot, id=advert_id)
        request.user.saved_plots.remove(plot)
        request.user.save()
        messages.success(request, "Pomyślnie usunięto ogłoszenie.")
    return redirect(request.META["HTTP_REFERER"])


@login_required
def save_all_adverts(request, advert_type: str):
    adverts = get_adverts(request, advert_type)
    for advert in adverts:
        request.user.saved_plots.add(advert)
    messages.success(request, "Pomyślnie zapisano wszystkie ogłoszenia.")
    return redirect(request.META["HTTP_REFERER"])


@login_required
def delete_all_adverts(request, advert_type: str, section: str = None):
    adverts = get_adverts(request, advert_type, user=request.user)
    for advert in adverts:
        request.user.saved_plots.remove(advert)
    messages.success(request, "Pomyślnie usunięto wszystkie ogłoszenia.")
    if section == "saved":
        return redirect(reverse("adverts:saved_plots"))
    return redirect(request.META["HTTP_REFERER"])


def download_csv(request, advert_type: str, section: str = None):
    user = None
    if section == "saved":
        user = request.user
    adverts = get_adverts(request, advert_type, user)
    rows = prepare_plot_to_csv(adverts)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows), content_type="text/csv"
    )
    response["Content-Disposition"] = 'attachment; filename="your_adverts.csv"'
    return response


def sending_csv(request, advert_type: str, section: str = None):
    user = None
    if section == "saved":
        user = request.user
    adverts = get_adverts(request, advert_type, user)
    rows = prepare_plot_to_csv(adverts)
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    [writer.writerow(row) for row in rows]
    recipient = request.user.email
    tasks.send_email.delay(
        subject="ParcelsScraper - wybrane działki",
        body="W załączeniu przesyłamy wybrane przez Ciebie działki.",
        to=[recipient],
        attachments=[("your_adverts.csv", csv_file.getvalue(), "text/csv")],
    )
    messages.success(
        request,
        "Wybrane działki zostały wysłane na adres email podany przy rejestracji.",
    )
    return redirect(request.META["HTTP_REFERER"])
