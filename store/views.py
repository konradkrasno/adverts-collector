import logging

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse

from .forms import SearchPlotForm
from .models import Plot
from .pagination import paginate
from .uploads import upload_plots


def upload_data(request):
    upload_plots()
    logging.info("Data successfully updated.")
    return JsonResponse({"OK": "Uploading data task pushed."})


def plot_search(request):
    form = SearchPlotForm(data_list=Plot.get_places())
    if request.method == "POST":
        form = SearchPlotForm(request.POST, data_list=Plot.get_places())
        if form.is_valid():
            return HttpResponseRedirect(
                reverse("store:plot_list", kwargs=form.cleaned_data)
            )
    return render(request, "store/plot/search.html", {"form": form})


def plot_list(
    request, place: str = None, price: int = None, area: int = None, query: str = None
):
    page = request.GET.get("page")
    object_list = Plot.manager.filter_plots(place, price, area, query)
    plots = paginate(object_list, page, 9)
    return render(request, "store/plot/list.html", {"plots": plots})


def plot_detail(request, plot_id: int):
    back_url = request.GET.get("back_url")
    plot = get_object_or_404(Plot, id=plot_id)
    return render(request, "store/plot/detail.html", {"plot": plot, "back_url": back_url})


def saved_plots_list(request):
    pass
