from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adicionar/', views.adicionar_contato, name='adicionar'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('listar/', views.listar_contatos, name='listar'),
]