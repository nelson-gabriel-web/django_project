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
    path('alterar-password/', views.alterar_password, name='alterar_password'),
    path('toggle-2fa/', views.toggle_2fa, name='toggle_2fa'),
    path('logout-all/', views.logout_all, name='logout_all'),
    path('termos/', views.termos, name='termos'),
    
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
    
    # Requisições de Compra
    path('requisicao/criar/', views.criar_requisicao, name='criar_requisicao'),
    path('requisicoes/', views.minhas_requisicoes, name='minhas_requisicoes'),
    path('requisicao/<int:requisicao_id>/', views.detalhe_requisicao, name='detalhe_requisicao'),
    path('requisicao/<int:requisicao_id>/cancelar/', views.cancelar_requisicao, name='cancelar_requisicao'),
    path('requisicoes/fornecedor/', views.requisicoes_fornecedor, name='requisicoes_fornecedor'),
    path('requisicao/<int:requisicao_id>/interessar/', views.interessar_requisicao, name='interessar_requisicao'),
    
    # Mapa
    path('mapa/', views.mapa_fornecedores, name='mapa_fornecedores'),
    
    # Transações
    path('dashboard/transacoes/', views.dashboard_transacoes, name='dashboard_transacoes'),

    # Pagamentos M-Pesa
    path('pagamento/iniciar/<int:transacao_id>/', views.iniciar_pagamento, name='iniciar_pagamento'),
    path('pagamento/confirmar/<int:transacao_id>/', views.confirmar_pagamento, name='confirmar_pagamento'),
    path('api/mpesa/callback/', views.callback_mpesa, name='callback_mpesa'),

    # Moderação
    path('moderador/dashboard/', views.dashboard_moderador, name='dashboard_moderador'),
    path('moderador/denuncia/<int:denuncia_id>/', views.detalhe_denuncia, name='detalhe_denuncia'),
    path('denunciar/<int:usuario_id>/', views.denunciar, name='denunciar'),

]