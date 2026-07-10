from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================================
# MODELOS EXISTENTES
# ============================================

class Contato(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome

class TentativaLogin(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tentativas = models.IntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    ultima_tentativa = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tentativas} tentativas"

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    
    # Dados Pessoais
    nome_completo = models.CharField(max_length=200, blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro'),
        ('prefiro_nao_dizer', 'Prefiro não dizer'),
    ])
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=30, blank=True, null=True, choices=[
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ])
    
    # Localização
    endereco = models.TextField(blank=True, null=True)
    nuit = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    
    # Canais de Comunicação
    email_comunicacao = models.BooleanField(default=True)
    whatsapp = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=True)
    
    # Status
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('cancelado', 'Cancelado'),
        ('em_analise', 'Em Análise'),
    ]
    status = models.CharField(max_length=20, default='ativo', choices=STATUS_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    # Indicações
    indicacoes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.username} - {self.status}"

    @property
    def antiguidade(self):
        """Calcula o tempo de casa em dias"""
        if self.data_cadastro:
            delta = timezone.now().date() - self.data_cadastro.date()
            return delta.days
        return 0

# ============================================
# MOEDAS PARA TRANSAÇÕES
# ============================================

class Moeda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nome = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    taxa_cambio = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.simbolo} ({self.nome})"

class PreferenciaMoeda(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferencia_moeda')
    moeda = models.ForeignKey(Moeda, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.moeda.codigo if self.moeda else 'Nenhuma'}"