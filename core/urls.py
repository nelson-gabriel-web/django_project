from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    # Splash e Home
    path('', views.splash, name='splash'),
    path('home/', views.home, name='home'),
    
    # Autenticação
    path('registar/', views.registar, name='registar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar/', views.recuperar_password, name='recuperar'),
    path('redefinir/<uidb64>/<token>/', views.redefinir_password, name='redefinir'),
    
    # Segurança
    path('alterar-password/', views.alterar_password, name='alterar_password'),
    path('toggle-2fa/', views.toggle_2fa, name='toggle_2fa'),
    path('logout-all/', views.logout_all, name='logout_all'),

    # Transações 
    path('transacoes/', views.minhas_transacoes, name='minhas_transacoes'),
    path('transacao/criar/<int:requisicao_id>/', views.criar_transacao, name='criar_transacao'),
    path('transacao/<int:transacao_id>/', views.detalhe_transacao, name='detalhe_transacao'),
    path('transacao/<int:transacao_id>/pagar/', views.pagar_transacao, name='pagar_transacao'),
    path('transacao/<int:transacao_id>/confirmar-envio/', views.confirmar_envio, name='confirmar_envio'),
    path('transacao/<int:transacao_id>/confirmar-rececao/', views.confirmar_rececao, name='confirmar_rececao'),
    path('transacao/<int:transacao_id>/disputa/', views.abrir_disputa, name='abrir_disputa'),
    path('dashboard/transacoes/', views.dashboard_transacoes, name='dashboard_transacoes'),
    
    # Contactos
    path('adicionar/', views.adicionar_contato, name='adicionar'),
    path('editar/<int:pk>/', views.editar_contato, name='editar'),
    path('excluir/<int:pk>/', views.excluir_contato, name='excluir'),
    path('listar/', views.listar_contatos, name='listar'),
    path('buscar/', views.buscar_contatos, name='buscar'),
    path('sucesso/', views.sucesso, name='sucesso'),
    
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    
    # Segurança
    path('dashboard/', views.dashboard_seguranca, name='dashboard_seguranca'),
    
    # Moedas
    path('moedas/', views.moedas_list, name='moedas_list'),
    path('moeda/definir/', views.definir_moeda_preferida, name='definir_moeda_preferida'),
    path('alternar-moeda/', views.alternar_moeda, name='alternar_moeda'),
    
    # Cliente
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('cliente/pedido/criar/', views.criar_pedido, name='criar_pedido'),
    path('cliente/pedidos/', views.meus_pedidos, name='meus_pedidos'),
    
    # Fornecedor
    path('fornecedor/dashboard/', views.dashboard_fornecedor, name='dashboard_fornecedor'),
    path('fornecedor/registar/', views.registar_fornecedor, name='registar_fornecedor'),
    path('fornecedor/pedidos/', views.pedidos_proximos, name='pedidos_proximos'),
    path('mapa/', views.mapa_fornecedores, name='mapa_fornecedores'),
    
    # Requisições de Compra
    path('requisicao/criar/', views.criar_requisicao, name='criar_requisicao'),
    path('requisicoes/', views.minhas_requisicoes, name='minhas_requisicoes'),
    path('requisicao/<int:requisicao_id>/', views.detalhe_requisicao, name='detalhe_requisicao'),
    path('requisicao/<int:requisicao_id>/cancelar/', views.cancelar_requisicao, name='cancelar_requisicao'),
    path('requisicoes/fornecedor/', views.requisicoes_fornecedor, name='requisicoes_fornecedor'),
    path('requisicao/<int:requisicao_id>/interessar/', views.interessar_requisicao, name='interessar_requisicao'),
]
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')