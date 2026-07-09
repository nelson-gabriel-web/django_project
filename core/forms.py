from django import forms
from .models import Contato, PerfilUsuario

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu telefone'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Digite seu endereço', 'rows': 3}),
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = [
            'nome_completo', 'idade', 'data_nascimento', 'genero',
            'nacionalidade', 'estado_civil', 'endereco', 'nuit',
            'cidade', 'pais', 'email_comunicacao', 'whatsapp',
            'sms', 'push_notification', 'foto'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua idade'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'nacionalidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua nacionalidade'}),
            'estado_civil': forms.Select(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Digite seu endereço'}),
            'nuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu NUIT'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua cidade'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu país'}),
            'email_comunicacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'whatsapp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notification': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
# ============================================
# FORMS PARA PLATAFORMA DE INTERMEDIAÇÃO
# ============================================

from .models import Pedido, Produto, Fornecedor

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['titulo', 'descricao', 'categoria', 'localizacao', 'orcamento', 'data_limite']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Preciso de um eletricista'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o que precisa...'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Maputo, Bairro Central'}),
            'orcamento': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor estimado (opcional)'}),
            'data_limite': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'categoria', 'preco', 'imagem', 'registado']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto/serviço'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço em €'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'registado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome_empresa', 'nif', 'telefone', 'endereco', 'cidade', 'raio_atuacao', 'descricao', 'categorias']
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa'}),
            'nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço completo'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'raio_atuacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Raio em km'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva a sua empresa'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }