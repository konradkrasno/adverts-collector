import logging

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .forms import SearchPlotForm
from .models import Plot
from .pagination import paginate
from .uploads import upload_plots


def upload_data(request):
    upload_plots()
    logging.info("Data successfully updated.")
    return JsonResponse({"OK": "Uploading data task pushed."})


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
        },
    )


def plot_detail(request, plot_id: int):
    plot = get_object_or_404(Plot, id=plot_id)
    return render(request, "adverts/plot/detail.html", {"plot": plot})


def saved_plots_list(request):
    pass
