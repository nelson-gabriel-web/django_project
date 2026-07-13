from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Contato, PerfilUsuario, Moeda, Categoria, Fornecedor,
    RequisicaoCompra, Transacao, Avaliacao, Denuncia
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    
    class Meta:
        model = PerfilUsuario
        fields = '__all__'

class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields = '__all__'
        read_only_fields = ['usuario', 'criado_em']

class MoedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moeda
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class FornecedorSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    
    class Meta:
        model = Fornecedor
        fields = '__all__'

class RequisicaoCompraSerializer(serializers.ModelSerializer):
    cliente = UserSerializer(read_only=True)
    moeda = MoedaSerializer(read_only=True)
    
    class Meta:
        model = RequisicaoCompra
        fields = '__all__'
        read_only_fields = ['cliente', 'data_criacao', 'data_atualizacao']

class TransacaoSerializer(serializers.ModelSerializer):
    cliente = UserSerializer(read_only=True)
    fornecedor = UserSerializer(read_only=True)
    
    class Meta:
        model = Transacao
        fields = '__all__'

class AvaliacaoSerializer(serializers.ModelSerializer):
    cliente = UserSerializer(read_only=True)
    fornecedor = UserSerializer(read_only=True)
    
    class Meta:
        model = Avaliacao
        fields = '__all__'

class DenunciaSerializer(serializers.ModelSerializer):
    denunciante = UserSerializer(read_only=True)
    fornecedor = UserSerializer(read_only=True)
    
    class Meta:
        model = Denuncia
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user