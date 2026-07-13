from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from . import views_api

# Router para os ViewSets
router = DefaultRouter()
router.register(r'moedas', views_api.MoedaViewSet, basename='moeda')
router.register(r'categorias', views_api.CategoriaViewSet, basename='categoria')
router.register(r'contactos', views_api.ContatoViewSet, basename='contato')
router.register(r'requisicoes', views_api.RequisicaoCompraViewSet, basename='requisicao')
router.register(r'fornecedores', views_api.FornecedorViewSet, basename='fornecedor')
router.register(r'transacoes', views_api.TransacaoViewSet, basename='transacao')
router.register(r'avaliacoes', views_api.AvaliacaoViewSet, basename='avaliacao')
router.register(r'perfil', views_api.PerfilUsuarioViewSet, basename='perfil')
router.register(r'denuncias', views_api.DenunciaViewSet, basename='denuncia')

urlpatterns = [
    # Autenticação JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Registo e perfil
    path('registar/', views_api.RegisterView.as_view(), name='api_registar'),
    path('me/', views_api.MeView.as_view(), name='api_me'),
    
    # API Router
    path('', include(router.urls)),
]