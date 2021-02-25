from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from .forms import UserRegistrationForm, UserEditForm


def dashboard(request):
    return render(request, "account/dashboard.html")


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            new_user.save()
            return HttpResponseRedirect(reverse("login"))
    user_form = UserRegistrationForm()
    return render(request, "account/register.html", {"user_form": user_form})


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Profil został pomyślnie zmieniony")
        else:
            messages.error(request, "Wystąpił błąd podczas edycji profilu")
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, "account/edit.html", {"user_form": user_form})
