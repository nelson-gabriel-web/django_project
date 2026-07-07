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
    # Recuperação de password
    path('recuperar/', views.recuperar_password, name='recuperar'),
    path('redefinir/<uidb64>/<token>/', views.redefinir_password, name='redefinir'),
# Sistema de Segurança
path('dashboard/', views.dashboard_seguranca, name='dashboard_seguranca'),
path('cameras/', views.cameras_list, name='cameras_list'),
path('cameras/adicionar/', views.adicionar_camera, name='adicionar_camera'),
path('eventos/', views.eventos_seguranca, name='eventos_seguranca'),
path('mapa-risco/', views.mapa_risco, name='mapa_risco'),
path('api/evento/', views.api_evento, name='api_evento'),
]