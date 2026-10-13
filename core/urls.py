from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path(
        'animal/<int:id>/',
        views.detalhes_animal,
        name='detalhes_animal'
    ),

    path(
        'login/',
        views.login_usuario,
        name='login'
    ),

    path(
    'logout/',
    views.logout_usuario,
    name='logout'
    ),

    path(
    'cadastro/',
    views.cadastro_usuario,
    name='cadastro'
    ),

    path(
    'animal/<int:id>/adotar/',
    views.solicitar_adocao,
    name='solicitar_adocao'
    ),
]