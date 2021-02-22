from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "account/index.html")


@login_required
def dashboard(request):
    return render(request, "account/dashboard.html")
