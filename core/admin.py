from django.contrib import admin
from .models import Contato, TentativaLogin, PerfilUsuario
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Contato, PerfilUsuario, Moeda, Categoria, Fornecedor, RequisicaoCompra, Transacao, HistoricoTransacao, TransacaoMpesa, Denuncia

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

# Criar grupo de moderadores (executar uma vez)
def criar_grupo_moderadores():
    grupo, created = Group.objects.get_or_create(name='Moderadores')
    if created:
        print('✅ Grupo "Moderadores" criado!')

# Registrar modelos no admin
admin.site.register(Contato)
admin.site.register(PerfilUsuario)
admin.site.register(Moeda)
admin.site.register(Categoria)
admin.site.register(Fornecedor)
admin.site.register(RequisicaoCompra)
admin.site.register(Transacao)
admin.site.register(HistoricoTransacao)
admin.site.register(TransacaoMpesa)
admin.site.register(Denuncia)