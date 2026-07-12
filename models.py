# ============================================
# SISTEMA UNIVERSAL DE TRANSAÇÕES
# ============================================

class Transacao(models.Model):
    TIPO_CHOICES = (
        ('produto', '📦 Produto'),
        ('veiculo', '🚗 Veículo'),
        ('imovel', '🏠 Imóvel'),
        ('servico', '🔧 Serviço'),
    )
    
    CATEGORIA_CHOICES = (
        ('eletronicos', 'Eletrônicos'),
        ('veiculos', 'Veículos'),
        ('imoveis', 'Imóveis'),
        ('servicos', 'Serviços'),
        ('moda', 'Moda e Acessórios'),
        ('alimentacao', 'Alimentação'),
        ('outros', 'Outros'),
    )
    
    STATUS_CHOICES = (
        ('pendente', '⏳ Aguardando Pagamento'),
        ('pago', '💰 Pago - Aguardando Envio'),
        ('enviado', '📦 Enviado - Aguardando Confirmacao'),
        ('confirmado', '✅ Confirmado - Aguardando Libertacao'),
        ('concluido', '🎉 Concluído'),
        ('cancelado', '❌ Cancelado'),
        ('reembolsado', '↩️ Reembolsado'),
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='produto')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='outros')
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes_cliente')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes_fornecedor')
    requisicao = models.ForeignKey('RequisicaoCompra', on_delete=models.SET_NULL, null=True, blank=True)
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    
    valor_total = models.DecimalField(max_digits=15, decimal_places=2)
    comissao = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_fornecedor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    codigo_confirmacao = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    prazo_confirmacao_dias = models.PositiveIntegerField(default=7)
    prazo_garantia_dias = models.PositiveIntegerField(default=7)
    
    veiculo_marca = models.CharField(max_length=100, blank=True, null=True)
    veiculo_modelo = models.CharField(max_length=100, blank=True, null=True)
    veiculo_ano = models.IntegerField(blank=True, null=True)
    veiculo_quilometragem = models.PositiveIntegerField(blank=True, null=True)
    veiculo_matricula = models.CharField(max_length=20, blank=True, null=True)
    veiculo_documento = models.FileField(upload_to='documentos_veiculos/', null=True, blank=True)
    
    imovel_tipo = models.CharField(max_length=50, blank=True, null=True)
    imovel_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    imovel_quartos = models.PositiveIntegerField(blank=True, null=True)
    imovel_banheiros = models.PositiveIntegerField(blank=True, null=True)
    imovel_endereco = models.TextField(blank=True, null=True)
    imovel_documento = models.FileField(upload_to='documentos_imoveis/', null=True, blank=True)
    
    codigo_rastreamento = models.CharField(max_length=50, blank=True, null=True)
    transportadora = models.CharField(max_length=100, blank=True, null=True)
    
    data_garantia_fim = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        from django.utils import timezone
        from datetime import timedelta
        
        if self.comissao == 0:
            if self.tipo == 'veiculo':
                self.comissao = self.valor_total * Decimal('0.03')
            elif self.tipo == 'imovel':
                self.comissao = self.valor_total * Decimal('0.02')
            elif self.tipo == 'servico':
                self.comissao = self.valor_total * Decimal('0.05')
            else:
                self.comissao = self.valor_total * Decimal('0.04')
            
            self.valor_fornecedor = self.valor_total - self.comissao
        
        if self.tipo == 'veiculo':
            self.prazo_confirmacao_dias = 15
            self.prazo_garantia_dias = 15
        elif self.tipo == 'imovel':
            self.prazo_confirmacao_dias = 30
            self.prazo_garantia_dias = 30
        else:
            self.prazo_confirmacao_dias = 7
            self.prazo_garantia_dias = 7
        
        if not self.codigo_confirmacao and self.status == 'pago':
            self.codigo_confirmacao = self.gerar_codigo()
        
        if self.status == 'confirmado' and not self.data_garantia_fim:
            self.data_garantia_fim = timezone.now() + timedelta(days=self.prazo_garantia_dias)
        
        super().save(*args, **kwargs)
    
    def gerar_codigo(self):
        import random
        return ''.join(random.choices('0123456789', k=6))
    
    def __str__(self):
        return f"TX-{self.id} | {self.tipo} | {self.cliente.username} → {self.fornecedor.username}"


class HistoricoTransacao(models.Model):
    """Registo de todas as alteracoes de uma transacao"""
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='historico')
    status_anterior = models.CharField(max_length=20)
    status_novo = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacao = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transacao.id}: {self.status_anterior} → {self.status_novo}"


class ComprovativoEnvio(models.Model):
    TIPO_CHOICES = (
        ('foto', '📸 Foto do Produto'),
        ('comprovativo', '📄 Comprovativo de Envio'),
        ('video', '🎥 Video do Embalamento'),
        ('codigo', '🔢 Codigo de Rastreamento'),
    )
    
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='comprovativos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    arquivo = models.FileField(upload_to='comprovativos/', null=True, blank=True)
    descricao = models.TextField(blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comprovativo {self.tipo} - TX-{self.transacao.id}"


class ProvaRececao(models.Model):
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='provas_rececao')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    foto_produto = models.ImageField(upload_to='provas_rececao/', null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prova de Rececao - TX-{self.transacao.id}"


class Disputa(models.Model):
    STATUS_CHOICES = (
        ('aberta', '🟡 Aberta'),
        ('em_analise', '🔵 Em Analise'),
        ('resolvida', '🟢 Resolvida'),
        ('rejeitada', '🔴 Rejeitada'),
    )
    
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='disputas')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputas_cliente')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputas_fornecedor')
    motivo = models.TextField()
    evidencia = models.FileField(upload_to='disputas/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    resolucao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Disputa #{self.id} - TX-{self.transacao.id}"


class Mediacao(models.Model):
    STATUS_CHOICES = (
        ('aberta', '🟡 Aberta'),
        ('em_analise', '🔵 Em Analise'),
        ('resolvida', '🟢 Resolvida'),
        ('rejeitada', '🔴 Rejeitada'),
    )
    
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='mediacoes')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mediacoes_cliente')
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mediacoes_fornecedor')
    motivo = models.TextField()
    evidencia_cliente = models.FileField(upload_to='mediacoes/', null=True, blank=True)
    evidencia_fornecedor = models.FileField(upload_to='mediacoes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    resolucao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Mediacao #{self.id} - TX-{self.transacao.id}"


class VerificacaoEspecial(models.Model):
    """Verificacao especial para veiculos e imoveis"""
    
    STATUS_CHOICES = (
        ('pendente', '⏳ Pendente'),
        ('aprovado', '✅ Aprovado'),
        ('reprovado', '❌ Reprovado'),
        ('em_analise', '🔍 Em Analise'),
    )
    
    transacao = models.ForeignKey(Transacao, on_delete=models.CASCADE, related_name='verificacoes')
    
    vistoria_feita = models.BooleanField(default=False)
    documento_veiculo_ok = models.BooleanField(default=False)
    multas_pendentes = models.BooleanField(default=False)
    
    documento_imovel_ok = models.BooleanField(default=False)
    dividas_pendentes = models.BooleanField(default=False)
    registro_atualizado = models.BooleanField(default=False)
    
    verificador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verificacoes_feitas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True, null=True)
    data_verificacao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Verificacao - TX-{self.transacao.id}"