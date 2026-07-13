from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Contato, PerfilUsuario, Moeda, Categoria, Fornecedor, RequisicaoCompra, Transacao, HistoricoTransacao, TransacaoMpesa, Denuncia

# Registrar modelos (apenas uma vez)
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

# Criar grupo de moderadores (executar apenas uma vez)
def criar_grupo_moderadores():
    grupo, created = Group.objects.get_or_create(name='Moderadores')
    if created:
        print('✅ Grupo "Moderadores" criado!')
    return grupo

# Executar a função quando o Django iniciar
criar_grupo_moderadores()