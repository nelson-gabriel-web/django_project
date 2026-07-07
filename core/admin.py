from django.contrib import admin
from .models import Contato, TentativaLogin

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'endereco', 'criado_em', 'usuario')
    search_fields = ('nome', 'telefone')

@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tentativas', 'bloqueado', 'ultima_tentativa')