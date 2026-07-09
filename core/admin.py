from django.contrib import admin
from .models import Contato, TentativaLogin

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'endereco', 'criado_em', 'usuario')
    search_fields = ('nome', 'telefone')

@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tentativas', 'bloqueado', 'ultima_tentativa')
from .models import Categoria, Fornecedor, Produto, Pedido, Transacao, Avaliacao, Notificacao

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'icone', 'criado_em')
    search_fields = ('nome',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'usuario', 'cidade', 'verificado', 'disponivel', 'avaliacao_media')
    search_fields = ('nome_empresa', 'usuario__username', 'cidade')
    list_filter = ('verificado', 'disponivel', 'categorias')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fornecedor', 'preco', 'disponivel', 'registado')
    search_fields = ('nome', 'fornecedor__nome_empresa')
    list_filter = ('disponivel', 'registado', 'categoria')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'categoria', 'status', 'criado_em')
    search_fields = ('titulo', 'cliente__username', 'localizacao')
    list_filter = ('status', 'categoria')

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cliente', 'fornecedor', 'valor', 'status', 'data_criacao')
    search_fields = ('pedido__titulo', 'cliente__username', 'fornecedor__nome_empresa')
    list_filter = ('status',)

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('transacao', 'nota', 'criado_em')
    list_filter = ('nota',)

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensagem', 'lida', 'criado_em')
    list_filter = ('lida',)
    search_fields = ('usuario__username', 'mensagem')