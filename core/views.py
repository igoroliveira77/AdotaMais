from django.shortcuts import render
from .models import Animal


def inicio(request):
    animais = Animal.objects.filter(status='Disponível')

    contexto = {
        'animais': animais
    }

    return render(request, 'core/inicio.html', contexto)

def detalhes_animal(request, id):
    animal = Animal.objects.get(id=id)

    contexto = {
        'animal': animal
    }

    return render(request, 'core/detalhes_animal.html', contexto)