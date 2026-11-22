from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import Animal, SolicitacaoAdocao, Favorito, MensagemContato, Notificacao
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.core.paginator import Paginator



def inicio(request):
    animais = Animal.objects.filter(status='Disponível')

    especie = request.GET.get('especie', '').strip()
    cidade = request.GET.get('cidade', '').strip()
    sexo = request.GET.get('sexo', '').strip()
    idade = request.GET.get('idade', '').strip()
    porte = request.GET.get('porte', '').strip()
    temperamento = request.GET.get('temperamento', '').strip()

    if especie:
        animais = animais.filter(especie=especie)

    if cidade:
        animais = animais.filter(cidade__icontains=cidade)

    if sexo:
        animais = animais.filter(sexo=sexo)

    if porte:
        animais = animais.filter(porte=porte)

    if temperamento:
        animais = animais.filter(temperamento=temperamento)

    if idade == 'filhote':
        animais = animais.filter(
            Q(unidade_idade='meses', idade__lte=12) |
            Q(unidade_idade='anos', idade__lte=1)
        )

    elif idade == 'jovem':
        animais = animais.filter(
            Q(unidade_idade='meses', idade__gt=12, idade__lte=60) |
            Q(unidade_idade='anos', idade__gte=2, idade__lte=5)
        )

    elif idade == 'adulto':
        animais = animais.filter(
            Q(unidade_idade='meses', idade__gt=60) |
            Q(unidade_idade='anos', idade__gt=5)
        )

    paginador = Paginator(animais, 6)

    numero_pagina = request.GET.get('page')

    animais = paginador.get_page(numero_pagina)

    especies = Animal.objects.filter(
        status='Disponível'
    ).values_list('especie', flat=True).distinct().order_by('especie')

    cidades = Animal.objects.filter(
        status='Disponível'
    ).values_list('cidade', flat=True).distinct().order_by('cidade')

    sexos = Animal.objects.filter(
    status='Disponível'
    ).values_list('sexo', flat=True).distinct().order_by('sexo')

    animais_favoritos = []
    total_notificacoes_nao_lidas = 0

    if request.user.is_authenticated:
        animais_favoritos = Favorito.objects.filter(
            usuario=request.user
        ).values_list('animal_id', flat=True)

        total_notificacoes_nao_lidas = Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()


    contexto = {
        'animais': animais,
        'animais_favoritos': animais_favoritos,
        'especies': especies,
        'cidades': cidades,
        'especie_selecionada': especie,
        'cidade_selecionada': cidade,
        'sexo_selecionado': sexo,
        'idade_selecionada': idade,
        'sexos': sexos,
        'porte_selecionado': porte,
        'temperamento_selecionado': temperamento,
        'portes': Animal.PORTE_CHOICES,
        'temperamentos': Animal.TEMPERAMENTO_CHOICES,
        'total_notificacoes_nao_lidas': total_notificacoes_nao_lidas,
        }

    return render(request, 'core/inicio.html', contexto)



def detalhes_animal(request, id):
    animal = Animal.objects.get(id=id)

    contexto = {
        'animal': animal
    }

    return render(request, 'core/detalhes_animal.html', contexto)
                  
@login_required(login_url='login')
def adicionar_favorito(request, id):
    if request.method != 'POST':
        return redirect('inicio')

    animal = get_object_or_404(Animal, id=id)

    favorito, criado = Favorito.objects.get_or_create(
        usuario=request.user,
        animal=animal
    )

    if criado:
        messages.success(request, 'Animal adicionado aos favoritos!')
    else:
        messages.info(request, 'Este animal já está nos seus favoritos.')

    return redirect('inicio')


@login_required(login_url='login')
def remover_favorito(request, id):
    if request.method != 'POST':
        return redirect('inicio')

    favorito = get_object_or_404(
        Favorito,
        usuario=request.user,
        animal_id=id
    )

    favorito.delete()

    messages.success(request, 'Animal removido dos favoritos!')

    pagina_origem = request.POST.get('pagina_origem')

    if pagina_origem == 'meus_favoritos':
        return redirect('meus_favoritos')

    return redirect('inicio')


@login_required(login_url='login')
def meus_favoritos(request):
    favoritos = Favorito.objects.filter(
        usuario=request.user
    ).select_related('animal').order_by('-data_adicao')
    total_favoritos = favoritos.count()

    contexto = {
        'favoritos': favoritos,
        'total_favoritos': total_favoritos,
    }

    return render(request, 'core/meus_favoritos.html', contexto)



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
def perfil_usuario(request):
    usuario = request.user

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'atualizar_perfil':
            usuario.first_name = request.POST.get('first_name', '').strip()
            usuario.last_name = request.POST.get('last_name', '').strip()
            usuario.email = request.POST.get('email', '').strip()

            usuario.save()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')

        elif acao == 'alterar_senha':
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if not usuario.check_password(senha_atual):
                messages.error(request, 'A senha atual está incorreta.')

            elif nova_senha != confirmar_senha:
                messages.error(request, 'As novas senhas não coincidem.')

            elif len(nova_senha) < 8:
                messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')

            else:
                usuario.set_password(nova_senha)
                usuario.save()

                update_session_auth_hash(request, usuario)

                messages.success(request, 'Senha alterada com sucesso!')

            return redirect('perfil')

    contexto = {
        'usuario': usuario,
        'total_solicitacoes': SolicitacaoAdocao.objects.filter(
            usuario=usuario
        ).count(),
        'total_favoritos': Favorito.objects.filter(
            usuario=usuario
        ).count(),
    }

    return render(request, 'core/perfil.html', contexto)

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
def minhas_notificacoes(request):
    notificacoes = Notificacao.objects.filter(
        usuario=request.user
    )

    total_nao_lidas = notificacoes.filter(lida=False).count()

    contexto = {
        'notificacoes': notificacoes,
        'total_nao_lidas': total_nao_lidas,
    }

    return render(
        request,
        'core/minhas_notificacoes.html',
        contexto
    )


@login_required(login_url='login')
def marcar_notificacao_lida(request, id):
    if request.method != 'POST':
        return redirect('minhas_notificacoes')

    notificacao = get_object_or_404(
        Notificacao,
        id=id,
        usuario=request.user
    )

    notificacao.lida = True
    notificacao.save(update_fields=['lida'])

    messages.success(request, 'Notificação marcada como lida!')

    return redirect('minhas_notificacoes')



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

def enviar_mensagem(request):
    if request.method != 'POST':
        return redirect('inicio')

    nome = request.POST.get('nome', '').strip()
    email = request.POST.get('email', '').strip()
    assunto = request.POST.get('assunto', '').strip()
    mensagem = request.POST.get('mensagem', '').strip()

    if not all([nome, email, assunto, mensagem]):
        messages.error(request, 'Preencha todos os campos.')
        return redirect('inicio')

    MensagemContato.objects.create(
        nome=nome,
        email=email,
        assunto=assunto,
        mensagem=mensagem
    )

    messages.success(
        request,
        'Mensagem enviada com sucesso! Obrigado pelo contato.'
    )

    return redirect('inicio')