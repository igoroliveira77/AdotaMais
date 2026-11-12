from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Animal, SolicitacaoAdocao
from django.contrib.admin.views.decorators import staff_member_required


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

            proxima_pagina = request.POST.get('next') or request.GET.get('next')

            if proxima_pagina and proxima_pagina.startswith('/'):
                return redirect(proxima_pagina)

            return redirect('inicio')

        return render(
            request,
            'core/login.html',
            {'erro': 'Usuário ou senha incorretos.'}
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

@login_required(login_url='login')
def solicitar_adocao(request, id):
    if request.method != 'POST':
        return redirect('detalhes_animal', id=id)

    animal = get_object_or_404(Animal, id=id, status='Disponível')

    solicitacao_existente = SolicitacaoAdocao.objects.filter(
        usuario=request.user,
        animal=animal
    ).exclude(
        status__in=['Recusada', 'Cancelada']
    ).exists()

    if solicitacao_existente:
        messages.warning(
            request,
            'Você já possui uma solicitação para este animal.'
        )
        return redirect('detalhes_animal', id=id)

    SolicitacaoAdocao.objects.create(
        usuario=request.user,
        animal=animal
    )

    messages.success(
        request,
        'Sua solicitação de adoção foi enviada com sucesso!'
    )

    return redirect('detalhes_animal', id=id)

@login_required(login_url='login')
def minhas_solicitacoes(request):
    solicitacoes = SolicitacaoAdocao.objects.filter(
        usuario=request.user
    ).select_related('animal').order_by('-data_solicitacao')

    solicitacoes_ativas = solicitacoes.filter(
        status__in=['Pendente', 'Em análise', 'Aprovada']
    )

    historico_solicitacoes = solicitacoes.filter(
        status__in=['Cancelada', 'Recusada']
    )

    contexto = {
        'solicitacoes_ativas': solicitacoes_ativas,
        'historico_solicitacoes': historico_solicitacoes,
    }

    return render(request, 'core/minhas_solicitacoes.html', contexto)

@login_required(login_url='login')
def cancelar_solicitacao(request, id):
    if request.method != 'POST':
        return redirect('minhas_solicitacoes')

    solicitacao = get_object_or_404(
        SolicitacaoAdocao,
        id=id,
        usuario=request.user
    )

    if solicitacao.status != 'Pendente':
        messages.warning(
            request,
            'Não é possível cancelar esta solicitação.'
        )
        return redirect('minhas_solicitacoes')

    solicitacao.status = 'Cancelada'
    solicitacao.save()

    messages.success(
        request,
        'Solicitação de adoção cancelada com sucesso!'
    )

    return redirect('minhas_solicitacoes')

@staff_member_required(login_url='login')
def painel_administrativo(request):

    contexto = {
        'total_animais': Animal.objects.count(),

        'animais_disponiveis': Animal.objects.filter(
            status='Disponível'
        ).count(),

        'animais_adotados': Animal.objects.filter(
            status='Adotado'
        ).count(),

        'solicitacoes_pendentes': SolicitacaoAdocao.objects.filter(
            status='Pendente'
        ).count(),

        'solicitacoes_em_analise': SolicitacaoAdocao.objects.filter(
            status='Em análise'
        ).count(),

        'solicitacoes_aprovadas': SolicitacaoAdocao.objects.filter(
            status='Aprovada'
        ).count(),

        'solicitacoes_recusadas': SolicitacaoAdocao.objects.filter(
            status='Recusada'
        ).count(),

        'solicitacoes_canceladas': SolicitacaoAdocao.objects.filter(
        status='Cancelada'
        ).count(),

        'ultimas_solicitacoes': SolicitacaoAdocao.objects.select_related(
            'usuario', 'animal'
        ).order_by('-data_solicitacao')[:5],

        'ultimos_animais': Animal.objects.order_by(
        '-data_cadastro'
        )[:5],
    }

    contexto['dados_grafico'] = {
        'labels': [
            'Pendente',
            'Em análise',
            'Aprovada',
            'Recusada',
            'Cancelada',
        ],
        'valores': [
            contexto['solicitacoes_pendentes'],
            contexto['solicitacoes_em_analise'],
            contexto['solicitacoes_aprovadas'],
            contexto['solicitacoes_recusadas'],
            contexto['solicitacoes_canceladas'],
        ],
    }

    return render(
        request,
        'core/painel_administrativo.html',
        contexto
    )