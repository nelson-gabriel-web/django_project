from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contato, PerfilUsuario, RequisicaoCompra, Moeda

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'telefone', 'endereco']

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = [
            'nome_completo', 'idade', 'data_nascimento', 'genero',
            'nacionalidade', 'estado_civil', 'cpf', 'nuit',
            'endereco', 'endereco_completo', 'bairro', 'cidade',
            'provincia', 'pais', 'telefone', 'tipo', 'foto',
            'receber_notificacoes', 'receber_emails', 'whatsapp', 'sms'
        ]
        widgets = {
            'data_nascimento': forms.SelectDateWidget(
                years=range(1900, 2026),
                attrs={'class': 'form-control', 'style': 'display: inline-block; width: auto; margin-right: 5px;'}
            ),
            'endereco': forms.Textarea(attrs={'rows': 3}),
            'endereco_completo': forms.Textarea(attrs={'rows': 3}),
        },
            'endereco': forms.Textarea(attrs={'rows': 3}),
            'endereco_completo': forms.Textarea(attrs={'rows': 3}),
        }

# ============================================
# FORMULÁRIO DE REQUISIÇÃO DE COMPRA
# ============================================

class RequisicaoCompraForm(forms.ModelForm):
    class Meta:
        model = RequisicaoCompra
        fields = [
            'titulo', 'descricao', 'categoria', 'quantidade',
            'valor_maximo', 'moeda', 'data_limite',
            'marca', 'modelo', 'ano', 'cor', 'condicao'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Descreva detalhadamente o que precisa comprar (marca, modelo, cor, especificações...)',
                'class': 'form-control'
            }),
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Ex: Toyota Fortuner 2025',
                'class': 'form-control'
            }),
            'quantidade': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
            'valor_maximo': forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'placeholder': 'Deixe em branco se for negociável',
                'class': 'form-control'
            }),
            'data_limite': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'Ex: Veículos, Eletrônicos, Alimentação...',
                'class': 'form-control'
            }),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carrega as moedas ativas, se existir
        if Moeda.objects.exists():
            self.fields['moeda'].queryset = Moeda.objects.filter(ativa=True)
        else:
            self.fields['moeda'].queryset = Moeda.objects.none()
            self.fields['moeda'].help_text = "Nenhuma moeda cadastrada ainda. Cadastre uma moeda primeiro."


# ============================================
# FORMULÁRIO PARA ALTERNAR MOEDA
# ============================================

class AlternarMoedaForm(forms.Form):
    moeda = forms.ModelChoiceField(
        queryset=Moeda.objects.filter(ativa=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        }),
        empty_label="Selecione uma moeda"
    )

# ============================================
# NOVOS FORMULÁRIOS ADICIONADOS
# ============================================

from .models import RequisicaoCompra, Moeda  # ADICIONE ESTA LINHA NO TOPO DO ARQUIVO

class RequisicaoCompraForm(forms.ModelForm):
    class Meta:
        model = RequisicaoCompra
        fields = [
            'titulo', 'descricao', 'categoria', 'quantidade',
            'valor_maximo', 'moeda', 'data_limite'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Descreva detalhadamente o que precisa comprar...',
                'class': 'form-control'
            }),
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Ex: Toyota Fortuner 2025',
                'class': 'form-control'
            }),
            'quantidade': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
            'valor_maximo': forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'placeholder': 'Deixe em branco se for negociável',
                'class': 'form-control'
            }),
            'data_limite': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'Ex: Veículos, Eletrônicos...',
                'class': 'form-control'
            }),
            'moeda': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Moeda.objects.exists():
            self.fields['moeda'].queryset = Moeda.objects.filter(ativa=True)