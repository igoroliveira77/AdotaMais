from django.shortcuts import render
from .models import Animal


def inicio(request):
    animais = Animal.objects.filter(status='Disponível')

    contexto = {
        'animais': animais
    }

    return render(request, 'core/inicio.html', contexto)