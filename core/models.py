from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

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
        ('em_analise', 'Em Analise'),
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
    nome_completo = models.CharField(max_length=200, blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True, choices=GENERO_CHOICES)
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=30, blank=True, null=True, choices=ESTADO_CIVIL_CHOICES)
    cpf = models.CharField(max_length=20, blank=True, null=True, help_text="NUIT ou Documento")
    nuit = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    endereco_completo = models.TextField(blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)
    ultimo_ip = models.GenericIPAddressField(null=True, blank=True)
    ultimo_dispositivo = models.CharField(max_length=200, blank=True, null=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    receber_notificacoes = models.BooleanField(default=True)
    receber_emails = models.BooleanField(default=True)
    email_comunicacao = models.BooleanField(default=True)
    whatsapp = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='ativo', choices=STATUS_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
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
    total_avaliacoes = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nome_empresa
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

class RequisicaoCompra(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Analise'),
        ('encontrado', 'Fornecedor Encontrado'),
        ('em_negociacao', 'Em Negociacao'),
        ('concluido', 'Concluido'),
        ('cancelado', 'Cancelado'),
    )
    CONDICAO_CHOICES = (
        ('novo', 'Novo'),
        ('usado', 'Usado'),
        ('seminovo', 'Seminovo'),
    )
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisicoes')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    cor = models.CharField(max_length=50, blank=True, null=True)
    condicao = models.CharField(max_length=20, choices=CONDICAO_CHOICES, blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    valor_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    moeda = models.ForeignKey(Moeda, on_delete=models.PROTECT, null=True, blank=True)
    endereco_entrega = models.TextField(blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_limite = models.DateTimeField(null=True, blank=True)
    fornecedores_interessados = models.ManyToManyField(User, related_name='requisicoes_interessadas', blank=True)
    fornecedor_escolhido = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisicoes_escolhidas')
    notificacoes_enviadas = models.BooleanField(default=False)
    data_notificacao = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Requisicao #{self.id} - {self.titulo}"
    def fornecedores_proximos(self):
        return User.objects.filter(perfilusuario__tipo='fornecedor', perfilusuario__status='ativo')[:10]
    def notificar_fornecedores(self):
        from django.core.mail import send_mail
        from django.conf import settings
        from datetime import datetime
        for fornecedor in self.fornecedores_proximos():
            if fornecedor.email:
                assunto = f"Nova Requisicao: {self.titulo}"
                mensagem = f"Cliente procura: {self.titulo}\nDescricao: {self.descricao}"
                send_mail(assunto, mensagem, settings.DEFAULT_FROM_EMAIL, [fornecedor.email], fail_silently=True)
        self.notificacoes_enviadas = True
        self.data_notificacao = datetime.now()
        self.save()

class Transacao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('confirmado', 'Confirmado'),
        ('concluido', 'Concluido'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes_cliente')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes_fornecedor')
    requisicao = models.ForeignKey(RequisicaoCompra, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2)
    comissao = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_fornecedor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    codigo_confirmacao = models.CharField(max_length=10, unique=True, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    def save(self, *args, **kwargs):
        from decimal import Decimal
        if self.comissao == 0:
            self.comissao = self.valor_total * Decimal('0.04')
            self.valor_fornecedor = self.valor_total - self.comissao
        if not self.codigo_confirmacao and self.status == 'pago':
            import random
            self.codigo_confirmacao = ''.join(random.choices('0123456789', k=6))
        super().save(*args, **kwargs)
    def __str__(self):
        return f"TX-{self.id} - {self.cliente.username} -> {self.fornecedor.username}"

class HistoricoTransacao(models.Model):
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='historico')
    status_anterior = models.CharField(max_length=20)
    status_novo = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacao = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.transacao.id}: {self.status_anterior} -> {self.status_novo}"

class TransacaoMpesa(models.Model):
    STATUS_CHOICES = (
        ('pending', '⏳ Pendente'),
        ('success', '✅ Sucesso'),
        ('failed', '❌ Falhou'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes_mpesa')
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, null=True, blank=True, related_name='pagamentos_mpesa')
    checkout_request_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resultado_descricao = models.TextField(blank=True, null=True)
    resultado_codigo = models.CharField(max_length=10, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"M-Pesa {self.id} - {self.phone_number} - {self.amount} MT"
    def mark_success(self):
        self.status = 'success'
        self.data_confirmacao = timezone.now()
        self.save()
    def mark_failed(self, motivo):
        self.status = 'failed'
        self.resultado_descricao = motivo
        self.save()

class Denuncia(models.Model):
    CATEGORIA_CHOICES = (
        ('drogas', '🚫 Drogas/Substâncias Ilícitas'),
        ('armas', '🔫 Armas e Munições'),
        ('falsificacao', '⚠️ Produto Contrafeito'),
        ('fraude', '💰 Fraude/Engano'),
        ('spam', '📧 Spam/Publicidade Indevida'),
        ('outros', '📌 Outros'),
    )
    STATUS_CHOICES = (
        ('pendente', '⏳ Pendente'),
        ('em_analise', '🔍 Em Análise'),
        ('aprovado', '✅ Aprovado'),
        ('rejeitado', '❌ Rejeitado'),
    )
    denunciante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='denuncias_feitas', null=True, blank=True)
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='denuncias_recebidas')
    produto = models.CharField(max_length=200, blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Denúncia #{self.id} - {self.denunciante.username}"

class Avaliacao(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    transacao = models.ForeignKey(Transacao, on_delete=models.SET_NULL, null=True, blank=True)
    nota = models.PositiveSmallIntegerField(choices=[(i, f'{i} ★') for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data_criacao']
        unique_together = ['cliente', 'transacao']
    def __str__(self):
        return f"{self.cliente.username} → {self.fornecedor.username}: {self.nota}★"