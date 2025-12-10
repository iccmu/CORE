from django.shortcuts import render


def fondos_home(request):
    return render(request, "fondos/home.html", {"app_name": "Fondos"})
