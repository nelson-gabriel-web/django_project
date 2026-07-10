from django.contrib import admin
from .models import Contato, TentativaLogin, PerfilUsuario

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'endereco', 'criado_em', 'usuario')
    search_fields = ('nome', 'telefone')

@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tentativas', 'bloqueado', 'ultima_tentativa')
    list_filter = ('bloqueado',)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'status', 'ativo_2fa', 'data_cadastro')
    list_filter = ('status', 'ativo_2fa')