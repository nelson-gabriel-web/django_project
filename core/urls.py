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
    
    # Contactos
    path('adicionar/', views.adicionar_contato, name='adicionar'),
    path('editar/<int:pk>/', views.editar_contato, name='editar'),
    path('excluir/<int:pk>/', views.excluir_contato, name='excluir'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('listar/', views.listar_contatos, name='listar'),
    path('buscar/', views.buscar_contatos, name='buscar'),
    
    # Recuperação de Password
    path('recuperar/', views.recuperar_password, name='recuperar'),
    path('redefinir/<uidb64>/<token>/', views.redefinir_password, name='redefinir'),
    
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    
    # Moedas
    path('moedas/', views.moedas_list, name='moedas_list'),
    path('moeda/definir/', views.definir_moeda_preferida, name='definir_moeda_preferida'),
]