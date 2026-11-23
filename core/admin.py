
from django.contrib import admin, messages
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import format_html

from .models import Animal, SolicitacaoAdocao, MensagemContato, Notificacao, Avaliacao

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
    'nome',
    'especie',
    'porte',
    'idade_com_unidade',
    'temperamento',
    'cidade',
    'status'
    )

    list_filter = (
        'especie',
        'porte',
        'temperamento',
        'status',
        'cidade'
    )

    search_fields = (
        'nome',
        'raca',
        'cidade',
        'observacoes_comportamento'
    )

    @admin.display(description='Idade')
    def idade_com_unidade(self, obj):
        return f'{obj.idade} {obj.unidade_idade}'


class SolicitacaoAdocaoForm(forms.ModelForm):

    class Meta:
        model = SolicitacaoAdocao
        fields = '__all__'

    def clean(self):
        dados = super().clean()

        animal = dados.get('animal')
        status = dados.get('status')

        if animal and status == 'Aprovada':

            outra_aprovada = SolicitacaoAdocao.objects.filter(
                animal=animal,
                status='Aprovada'
            ).exclude(pk=self.instance.pk).exists()

            if outra_aprovada:
                raise ValidationError(
                    'Este animal já possui uma adoção aprovada.'
                )

            if animal.status != 'Disponível':
                raise ValidationError(
                    'Este animal não está disponível para adoção.'
                )

        return dados


@admin.register(SolicitacaoAdocao)
class SolicitacaoAdocaoAdmin(admin.ModelAdmin):
    form = SolicitacaoAdocaoForm

    list_display = ('usuario', 'animal', 'data_solicitacao', 'status')
    list_filter = ('status', 'data_solicitacao')
    search_fields = ('usuario__username', 'animal__nome')
    readonly_fields = ('data_solicitacao',)

    actions = ['aprovar_solicitacoes']

    @admin.action(description='Aprovar solicitações selecionadas')
    def aprovar_solicitacoes(self, request, queryset):

        solicitacoes = list(queryset.select_related('animal'))

        if not solicitacoes:
            return

        animais_ids = [s.animal_id for s in solicitacoes]

        if len(animais_ids) != len(set(animais_ids)):
            self.message_user(
                request,
                'Selecione apenas uma solicitação por animal.',
                level=messages.ERROR
            )
            return

        with transaction.atomic():

            animais = {
                animal.pk: animal
                for animal in Animal.objects.select_for_update().filter(
                    pk__in=animais_ids
                )
            }

            for solicitacao in solicitacoes:

                animal = animais.get(solicitacao.animal_id)

                if solicitacao.status not in ['Pendente', 'Em análise']:
                    self.message_user(
                        request,
                        'Existem solicitações que não podem ser aprovadas.',
                        level=messages.ERROR
                    )
                    return

                if animal is None or animal.status != 'Disponível':
                    self.message_user(
                        request,
                        'Um ou mais animais não estão disponíveis para adoção.',
                        level=messages.ERROR
                    )
                    return

                outra_aprovada = SolicitacaoAdocao.objects.filter(
                    animal_id=solicitacao.animal_id,
                    status='Aprovada'
                ).exists()

                if outra_aprovada:
                    self.message_user(
                        request,
                        'Um ou mais animais já possuem adoção aprovada.',
                        level=messages.ERROR
                    )
                    return
            
            for solicitacao in solicitacoes:
                solicitacao.status = 'Aprovada'
                solicitacao.save(update_fields=['status'])

                Animal.objects.filter(
                    pk=solicitacao.animal_id
                ).update(status='Adotado')

                Notificacao.objects.create(
                    usuario=solicitacao.usuario,
                    solicitacao=solicitacao,
                    mensagem=f'Sua solicitação para {solicitacao.animal.nome} foi aprovada!'
                )

        self.message_user(
            request,
            'Solicitações aprovadas com sucesso!',
            level=messages.SUCCESS
        )


    def save_model(self, request, obj, form, change):
        with transaction.atomic():

            status_anterior = None
            animal_anterior_id = None

            if change:
                anterior = SolicitacaoAdocao.objects.get(pk=obj.pk)
                status_anterior = anterior.status
                animal_anterior_id = anterior.animal_id

            super().save_model(request, obj, form, change)

            if obj.status == 'Aprovada':
                Animal.objects.filter(pk=obj.animal_id).update(
                    status='Adotado'
                )

            if (
                status_anterior == 'Aprovada'
                and (
                    obj.status != 'Aprovada'
                    or animal_anterior_id != obj.animal_id
                )
            ):
                outra_aprovada = SolicitacaoAdocao.objects.filter(
                    animal_id=animal_anterior_id,
                    status='Aprovada'
                ).exists()

                if not outra_aprovada:
                    Animal.objects.filter(
                        pk=animal_anterior_id
                    ).update(status='Disponível')

            if change and status_anterior != obj.status:
                mensagens = {
                    'Em análise': f'Sua solicitação para {obj.animal.nome} está em análise.',
                    'Aprovada': f'Sua solicitação para {obj.animal.nome} foi aprovada!',
                    'Recusada': f'Sua solicitação para {obj.animal.nome} foi recusada.',
                    'Cancelada': f'Sua solicitação para {obj.animal.nome} foi cancelada.',
                }

                mensagem = mensagens.get(obj.status)

                if mensagem:
                    Notificacao.objects.create(
                        usuario=obj.usuario,
                        solicitacao=obj,
                        mensagem=mensagem
                    )



@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'email',
        'assunto',
        'status_visual',
        'data_envio',
    )

    list_filter = ('status', 'data_envio')

    search_fields = (
        'nome',
        'email',
        'assunto',
        'mensagem',
    )

    readonly_fields = ('data_envio',)

    @admin.display(description='Status', ordering='status')
    def status_visual(self, obj):
        cores = {
            'Não lida': '#dc3545',
            'Lida': '#0d6efd',
            'Respondida': '#198754',
        }

        cor = cores.get(obj.status, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 10px; border-radius: 12px; font-weight: bold;">'
            '{}</span>',
            cor,
            obj.status
        )

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):

    list_display = (
        'solicitacao',
        'nota',
        'comentario',
        'data_avaliacao',
    )

    list_filter = (
        'nota',
        'data_avaliacao',
    )

    search_fields = (
        'solicitacao__usuario__username',
        'solicitacao__animal__nome',
        'comentario',
    )

    readonly_fields = ('data_avaliacao',)