from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import (
    Contato, PerfilUsuario, Moeda, Categoria, Fornecedor,
    RequisicaoCompra, Transacao, Avaliacao, Denuncia
)
from .serializers import (
    UserSerializer, PerfilUsuarioSerializer, ContatoSerializer,
    MoedaSerializer, CategoriaSerializer, FornecedorSerializer,
    RequisicaoCompraSerializer, TransacaoSerializer,
    AvaliacaoSerializer, DenunciaSerializer, RegisterSerializer
)

# ============================================
# VIEWSETS DA API
# ============================================

class MoedaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listar moedas disponíveis"""
    queryset = Moeda.objects.filter(ativa=True)
    serializer_class = MoedaSerializer
    permission_classes = [AllowAny]

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Listar categorias"""
    queryset = Categoria.objects.filter(ativo=True)
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

class ContatoViewSet(viewsets.ModelViewSet):
    """CRUD de contactos"""
    serializer_class = ContatoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Contato.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class RequisicaoCompraViewSet(viewsets.ModelViewSet):
    """CRUD de requisições de compra"""
    serializer_class = RequisicaoCompraSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RequisicaoCompra.objects.filter(cliente=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class FornecedorViewSet(viewsets.ReadOnlyModelViewSet):
    """Listar fornecedores"""
    queryset = Fornecedor.objects.filter(ativo=True)
    serializer_class = FornecedorSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        fornecedor = self.get_object()
        avaliacoes = Avaliacao.objects.filter(fornecedor=fornecedor.usuario)
        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)

class TransacaoViewSet(viewsets.ModelViewSet):
    """CRUD de transações"""
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transacao.objects.filter(
            cliente=self.request.user
        ) | Transacao.objects.filter(
            fornecedor=self.request.user
        )

class AvaliacaoViewSet(viewsets.ModelViewSet):
    """CRUD de avaliações"""
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Avaliacao.objects.filter(
            cliente=self.request.user
        ) | Avaliacao.objects.filter(
            fornecedor=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de perfil do utilizador"""
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PerfilUsuario.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class DenunciaViewSet(viewsets.ModelViewSet):
    """CRUD de denúncias"""
    serializer_class = DenunciaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Denuncia.objects.filter(denunciante=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(denunciante=self.request.user)

# ============================================
# VIEWS DE AUTENTICAÇÃO
# ============================================

class RegisterView(generics.CreateAPIView):
    """Registo de novos utilizadores"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Criar perfil automaticamente
        PerfilUsuario.objects.create(
            usuario=user,
            tipo='cliente',
            nome_completo=f"{user.first_name} {user.last_name}".strip() or user.username
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Utilizador criado com sucesso!'
        }, status=status.HTTP_201_CREATED)

class MeView(generics.RetrieveUpdateAPIView):
    """Obter/atualizar dados do utilizador autenticado"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user