from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path(
    'enviar-mensagem/',
    views.enviar_mensagem,
    name='enviar_mensagem'
    ),

    path(
    'painel-administrativo/',
    views.painel_administrativo,
    name='painel_administrativo'
    ),

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
    'perfil/',
    views.perfil_usuario,
    name='perfil'
    ),

        path(
        'excluir-conta/',
        views.excluir_conta,
        name='excluir_conta'
    ),

    path(
    'animal/<int:id>/adotar/',
    views.solicitar_adocao,
    name='solicitar_adocao'
    ),

    path(
    'minhas-solicitacoes/',
    views.minhas_solicitacoes,
    name='minhas_solicitacoes'
    ),

    path(
    'solicitacao/<int:id>/avaliar/',
    views.avaliar_adocao,
    name='avaliar_adocao'
    ),

    path(
    'solicitacao/<int:id>/cancelar/',
    views.cancelar_solicitacao,
    name='cancelar_solicitacao'
    ),

        path(
        'animal/<int:id>/favoritar/',
        views.adicionar_favorito,
        name='adicionar_favorito'
    ),

    path(
        'animal/<int:id>/remover-favorito/',
        views.remover_favorito,
        name='remover_favorito'
    ),

    path(
    'meus-favoritos/',
    views.meus_favoritos,
    name='meus_favoritos'
    ),


    path(
        'notificacoes/',
        views.minhas_notificacoes,
        name='minhas_notificacoes'
    ),

    path(
        'notificacao/<int:id>/ler/',
        views.marcar_notificacao_lida,
        name='marcar_notificacao_lida'
    ),

]