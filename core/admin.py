from django.contrib import admin
from .models import Animal, SolicitacaoAdocao


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'cidade', 'status')
    list_filter = ('especie', 'status', 'cidade')
    search_fields = ('nome', 'raca', 'cidade')


@admin.register(SolicitacaoAdocao)
class SolicitacaoAdocaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'animal', 'data_solicitacao', 'status')
    list_filter = ('status', 'data_solicitacao')
    search_fields = ('usuario__username', 'animal__nome')
    readonly_fields = ('data_solicitacao',)