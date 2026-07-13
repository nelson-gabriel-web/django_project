from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Contato, PerfilUsuario, Moeda, Categoria, Fornecedor, RequisicaoCompra, Transacao, HistoricoTransacao, TransacaoMpesa, Denuncia, Avaliacao, TermosAceitacao

# Registrar modelos
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
admin.site.register(Avaliacao)
admin.site.register(TermosAceitacao)

# Função para criar grupo de moderadores (executada apenas uma vez)
def criar_grupo_moderadores():
    try:
        grupo, created = Group.objects.get_or_create(name='Moderadores')
        if created:
            print('✅ Grupo "Moderadores" criado!')
        return grupo
    except:
        # Se a base de dados ainda não estiver pronta, ignora
        pass

# Executar a função
criar_grupo_moderadores()