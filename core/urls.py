from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('animal/<int:id>/', views.detalhes_animal, name='detalhes_animal'),
]