from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Contato
from django import forms
from .models import PerfilUsuario

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

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
        labels = {
            'nome_completo': 'Nome Completo',
            'data_nascimento': 'Data de Nascimento',
            'estado_civil': 'Estado Civil',
            'email_comunicacao': 'E-mail',
            'whatsapp': 'WhatsApp',
            'sms': 'SMS',
            'push_notification': 'Push Notification',
        }