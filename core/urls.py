from django.urls import path
from . import views

urlpatterns = [
    path('', views.splash, name='splash'),
    path('home/', views.home, name='home'),
    path('registar/', views.registar, name='registar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('adicionar/', views.adicionar_contato, name='adicionar'),
    path('editar/<int:pk>/', views.editar_contato, name='editar'),
    path('excluir/<int:pk>/', views.excluir_contato, name='excluir'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('listar/', views.listar_contatos, name='listar'),
    path('buscar/', views.buscar_contatos, name='buscar'),
    path('recuperar/', views.recuperar_password, name='recuperar'),
    path('redefinir/<uidb64>/<token>/', views.redefinir_password, name='redefinir'),
    path('dashboard/', views.dashboard_seguranca, name='dashboard_seguranca'),
    path('comunidades/', views.comunidades_list, name='comunidades_list'),
    path('comunidade/adicionar/', views.adicionar_comunidade, name='adicionar_comunidade'),
    path('comunidade/<int:pk>/', views.comunidade_detalhe, name='comunidade_detalhe'),
    path('comunidade/<int:comunidade_pk>/crime/adicionar/', views.adicionar_crime, name='adicionar_crime'),
    path('comunidade/<int:comunidade_pk>/estrategia/adicionar/', views.adicionar_estrategia, name='adicionar_estrategia'),
    path('comunidade/<int:comunidade_pk>/avaliar/', views.avaliar_seguranca, name='avaliar_seguranca'),
    path('comunidade/relatorio/<int:pk>/', views.relatorio_comunidade, name='relatorio_comunidade'),
    path('api/evento/', views.api_evento, name='api_evento'),
path('perfil/', views.perfil, name='perfil'),
]