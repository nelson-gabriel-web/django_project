from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

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
    TIPO_USUARIO = (
        ('cliente', 'Cliente'),
        ('fornecedor', 'Fornecedor'),
        ('admin', 'Administrador'),
    )
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('cancelado', 'Cancelado'),
        ('em_analise', 'Em Análise'),
    ]
    
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro'),
        ('prefiro_nao_dizer', 'Prefiro não dizer'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='cliente')
    
    # Dados Pessoais
    nome_completo = models.CharField(max_length=200, blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True, choices=GENERO_CHOICES)
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=30, blank=True, null=True, choices=ESTADO_CIVIL_CHOICES)
    
    # Documentos
    cpf = models.CharField(max_length=20, blank=True, null=True, help_text="NUIT ou Documento")
    nuit = models.CharField(max_length=20, blank=True, null=True)
    
    # Localização
    endereco = models.TextField(blank=True, null=True)
    endereco_completo = models.TextField(blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True)
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    
    # Canais de Comunicação
    receber_notificacoes = models.BooleanField(default=True)
    receber_emails = models.BooleanField(default=True)
    email_comunicacao = models.BooleanField(default=True)
    whatsapp = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=True)
    
    # Status
    status = models.CharField(max_length=20, default='ativo', choices=STATUS_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    # Indicações
    indicacoes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.status}"

    @property
    def antiguidade(self):
        if self.data_cadastro:
            delta = timezone.now().date() - self.data_cadastro.date()
            return delta.days
        return 0
    
    def is_fornecedor(self):
        return self.tipo == 'fornecedor'


# ============================================
# MOEDAS PARA TRANSAÇÕES
# ============================================

class Moeda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nome = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    taxa_cambio = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    ativa = models.BooleanField(default=True)
    padrao = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.simbolo} ({self.nome})"
    
    def formatar(self, valor):
        return f"{self.simbolo} {valor:,.2f}".replace(",", ".")

class PreferenciaMoeda(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferencia_moeda')
    moeda = models.ForeignKey(Moeda, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.moeda.codigo if self.moeda else 'Nenhuma'}"


# ============================================
# NOVOS MODELOS ADICIONADOS
# ============================================

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.CharField(max_length=50, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"


class Fornecedor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fornecedor')
    nome_empresa = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20)
    telefone_alternativo = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    endereco = models.TextField()
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    raio_entrega_km = models.PositiveIntegerField(default=10)
    
    ativo = models.BooleanField(default=True)
    tem_estoque = models.BooleanField(default=True)
    horario_funcionamento = models.CharField(max_length=200, blank=True, null=True)
    tempo_entrega = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: 1-2 dias")
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome_empresa
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"


class RequisicaoCompra(models.Model):
    STATUS_CHOICES = (
        ('pendente', '🟡 Pendente'),
        ('em_analise', '🔵 Em Análise'),
        ('encontrado', '🟢 Fornecedor Encontrado'),
        ('em_negociacao', '🟣 Em Negociação'),
        ('concluido', '✅ Concluído'),
        ('cancelado', '❌ Cancelado'),
    )
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisicoes')
    titulo = models.CharField(max_length=200, help_text="Ex: Toyota Fortuner 2025")
    descricao = models.TextField(help_text="Descrição detalhada do que precisa comprar")
    categoria = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: Veículos, Eletrônicos, etc")
    
    quantidade = models.PositiveIntegerField(default=1)
    valor_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Valor máximo que pretende pagar (MT)")
    moeda = models.ForeignKey(Moeda, on_delete=models.PROTECT, null=True, blank=True)
    
    endereco_entrega = models.TextField(blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_limite = models.DateTimeField(null=True, blank=True, help_text="Data limite para encontrar fornecedor")
    
    fornecedores_interessados = models.ManyToManyField(User, related_name='requisicoes_interessadas', blank=True)
    fornecedor_escolhido = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisicoes_escolhidas')
    
    notificacoes_enviadas = models.BooleanField(default=False)
    data_notificacao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Requisição #{self.id} - {self.titulo}"
    
    def fornecedores_proximos(self):
        fornecedores = User.objects.filter(
            perfilusuario__tipo='fornecedor',
            perfilusuario__status='ativo'
        )
        if self.provincia:
            fornecedores = fornecedores.filter(
                perfilusuario__provincia__icontains=self.provincia
            )
        return fornecedores[:10]
    
    def notificar_fornecedores(self):
        from django.core.mail import send_mail
        from django.conf import settings
        from datetime import datetime
        
        fornecedores = self.fornecedores_proximos()
        
        for fornecedor in fornecedores:
            if fornecedor.email:
                assunto = f"🔔 Nova Requisição: {self.titulo}"
                mensagem = f"""
Olá {fornecedor.perfilusuario.nome_completo or fornecedor.username}!

Um cliente está procurando: {self.titulo}

📝 Descrição: {self.descricao}
📦 Quantidade: {self.quantidade}
💰 Valor máximo: {self.valor_maximo or 'A negociar'} MT
📍 Localização: {self.cidade}, {self.provincia}

Acesse a plataforma Nhonga para mais detalhes.

Atenciosamente,
Equipe Nhonga
"""
                
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [fornecedor.email],
                    fail_silently=True,
                )
        
        self.notificacoes_enviadas = True
        self.data_notificacao = datetime.now()
        self.save()
# ============================================
# SISTEMA DE AVALIAÇÕES
# ============================================

class Avaliacao(models.Model):
    """Avaliação de fornecedores por clientes"""
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    requisicao = models.ForeignKey(RequisicaoCompra, on_delete=models.CASCADE, null=True, blank=True)
    nota = models.PositiveSmallIntegerField(choices=[(i, f'{i} ★') for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cliente.username} → {self.fornecedor.username}: {self.nota}★"
    
    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_criacao']