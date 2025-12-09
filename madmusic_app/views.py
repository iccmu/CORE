from django.shortcuts import render
from core.models import Proyecto

def madmusic_home(request):
    proyecto = Proyecto.objects.filter(slug="madmusic").first()
    return render(request, "madmusic/home.html", {
        "proyecto": proyecto,
        "app_name": "Madmusic"
    })
