from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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


def login_usuario(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            login(request, usuario)

            return redirect('inicio')

        else:

            return render(
                request,
                'core/login.html',
                {
                    'erro': 'Usuário ou senha incorretos.'
                }
            )

    return render(request, 'core/login.html')

def logout_usuario(request):
    logout(request)
    return redirect('inicio')

def cadastro_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(
                request,
                'core/cadastro.html',
                {'erro': 'As senhas não são iguais.'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'core/cadastro.html',
                {'erro': 'Esse usuário já existe.'}
            )

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, usuario)

        return redirect('inicio')

    return render(request, 'core/cadastro.html')