from django.shortcuts import render


def error_404(request, exception):
    return render(request, "errors/404.html", locals())


def error_500(request, exception=None):
    return render(request, "errors/500.html", locals())
