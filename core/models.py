from django.db import models
from django.contrib.auth.models import User


class Contato(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nome

# NOVO MODELO PARA CONTAR TENTATIVAS DE LOGIN
class TentativaLogin(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tentativas = models.IntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    ultima_tentativa = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tentativas} tentativas"

# ============================================
# MODELOS PARA SISTEMA DE SEGURANÇA
# ============================================

class Camera(models.Model):
    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=255)
    url_rtsp = models.URLField(max_length=500, blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.localizacao}"

class SensorMovimento(models.Model):
    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[
        ('pir', 'PIR'),
        ('ultrassom', 'Ultrassom'),
        ('laser', 'Laser'),
    ])
    ativo = models.BooleanField(default=True)
    ultimo_evento = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.localizacao}"

class EventoSeguranca(models.Model):
    TIPOS = [
        ('movimento', 'Movimento Detectado'),
        ('porta_aberta', 'Porta Aberta'),
        ('janela_aberta', 'Janela Aberta'),
        ('alarme', 'Alarme Disparado'),
        ('face_detectada', 'Face Detectada'),
        ('comportamento_suspeito', 'Comportamento Suspeito'),
    ]
    
    tipo = models.CharField(max_length=30, choices=TIPOS)
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    sensor = models.ForeignKey(SensorMovimento, on_delete=models.SET_NULL, null=True, blank=True)
    imagem = models.ImageField(upload_to='eventos/', null=True, blank=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    processado = models.BooleanField(default=False)
    alerta_enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.criado_em}"

class ZonaRisco(models.Model):
    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=255)
    nivel_risco = models.IntegerField(default=1, choices=[(1, 'Baixo'), (2, 'Médio'), (3, 'Alto'), (4, 'Crítico')])
    eventos = models.IntegerField(default=0)
    ultimo_evento = models.DateTimeField(null=True, blank=True)
    coordenadas = models.JSONField(default=dict)  # Lat, Long

    def __str__(self):
        return f"{self.nome} - Risco: {self.get_nivel_risco_display()}"

class Alerta(models.Model):
    TIPOS = [
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('sms', 'SMS'),
    ]
    evento = models.ForeignKey(EventoSeguranca, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    mensagem = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)
    lido = models.BooleanField(default=False)

    def __str__(self):
        return f"Alerta {self.tipo} - {self.enviado_em}"
class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

# ============================================
# MODELOS PARA ANÁLISE COMUNITÁRIA DE SEGURANÇA
# ============================================

class Comunidade(models.Model):
    """Representa uma comunidade/bairro"""
    nome = models.CharField(max_length=200)
    localizacao = models.CharField(max_length=255)
    coordenadas = models.JSONField(default=dict)  # {lat: , lng: }
    populacao_estimada = models.IntegerField(default=0)
    numero_residencias = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Crime(models.Model):
    """Registo de crimes ocorridos na comunidade"""
    TIPOS_CRIME = [
        ('roubo_residencia', 'Roubo a Residência'),
        ('roubo_veiculo', 'Roubo de Veículo'),
        ('assalto_pessoa', 'Assalto a Pessoa'),
        ('furto', 'Furto'),
        ('vandalismo', 'Vandalismo'),
        ('violencia_domestica', 'Violência Doméstica'),
        ('trafico_drogas', 'Tráfico de Drogas'),
        ('homicidio', 'Homicídio'),
        ('outro', 'Outro'),
    ]
    
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPOS_CRIME)
    descricao = models.TextField()
    data_ocorrencia = models.DateTimeField()
    localizacao = models.CharField(max_length=255)
    coordenadas = models.JSONField(default=dict)
    vitima = models.CharField(max_length=100, blank=True, null=True)
    suspeito = models.CharField(max_length=100, blank=True, null=True)
    registado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.data_ocorrencia.strftime('%d/%m/%Y')}"

class EstrategiaSeguranca(models.Model):
    """Estratégias de proteção adotadas pelos moradores"""
    TIPOS_ESTRATEGIA = [
        ('policia_comunitaria', 'Polícia Comunitária'),
        ('vigilancia_vizinhos', 'Vigilância Rotativa entre Vizinhos'),
        ('camera_seguranca', 'Câmaras de Segurança'),
        ('iluminacao', 'Iluminação Pública'),
        ('alarme', 'Sistemas de Alarme'),
        ('guarda_patrimonial', 'Guarda Patrimonial'),
        ('grupo_whatsapp', 'Grupo de WhatsApp'),
        ('patrulha_voluntaria', 'Patrulha Voluntária'),
        ('outro', 'Outro'),
    ]
    
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPOS_ESTRATEGIA)
    descricao = models.TextField()
    ativa = models.BooleanField(default=True)
    data_implementacao = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.comunidade.nome}"

class PercepcaoSeguranca(models.Model):
    """Percepção de segurança dos moradores"""
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE)
    nivel_seguranca = models.IntegerField(choices=[
        (1, 'Muito Inseguro'),
        (2, 'Inseguro'),
        (3, 'Neutro'),
        (4, 'Seguro'),
        (5, 'Muito Seguro')
    ])
    principais_medos = models.TextField()
    sugestoes = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comunidade.nome} - Nível: {self.nivel_seguranca}"

class RelatorioComunidade(models.Model):
    """Relatórios gerados sobre a comunidade"""
    comunidade = models.ForeignKey(Comunidade, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    dados = models.JSONField(default=dict)  # Dados estruturados do relatório
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} - {self.criado_em.strftime('%d/%m/%Y')}"

# ============================================
# MODELOS PARA 2FA (DOIS FATORES)
# ============================================

class PerfilUsuario(models.Model):
    """Extensão do modelo User para 2FA"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - 2FA: {'Ativo' if self.ativo_2fa else 'Inativo'}"

class PerfilUsuario(models.Model):
    # ========== DADOS PESSOAIS ==========
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
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
    
    # ========== LOCALIZAÇÃO ==========
    endereco = models.TextField(blank=True, null=True)
    nuit = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    
    # ========== CANAIS DE COMUNICAÇÃO ==========
    email_comunicacao = models.BooleanField(default=True)
    whatsapp = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=True)
    
    # ========== STATUS E ANTIGUIDADE ==========
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('cancelado', 'Cancelado'),
        ('em_analise', 'Em Análise'),
    ]
    status = models.CharField(max_length=20, default='ativo', choices=STATUS_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    # ========== INDICAÇÕES ==========
    indicacoes = models.IntegerField(default=0)
    
    # ========== 2FA ==========
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)
    
    # ========== FOTO ==========
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.status}"

    @property
    def antiguidade(self):
        """Calcula o tempo de casa em dias"""
        from django.utils.timezone import now
        if self.data_cadastro:
            delta = now().date() - self.data_cadastro.date()
            return delta.days
        return 0

# ============================================
# MODELOS PARA PLATAFORMA DE INTERMEDIAÇÃO NHONGA
# ============================================

class Categoria(models.Model):
    """Categorias de produtos/serviços"""
    nome = models.CharField(max_length=100, unique=True)
    icone = models.CharField(max_length=50, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    """Fornecedor que oferece produtos/serviços"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fornecedor')
    nome_empresa = models.CharField(max_length=200)
    nif = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    coordenadas = models.JSONField(default=dict)
    raio_atuacao = models.IntegerField(default=10)
    descricao = models.TextField(blank=True, null=True)
    categorias = models.ManyToManyField(Categoria, related_name='fornecedores')
    verificado = models.BooleanField(default=False)
    disponivel = models.BooleanField(default=True)
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_avaliacoes = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome_empresa} - {self.usuario.username}"

class Produto(models.Model):
    """Produto ou serviço oferecido pelo fornecedor"""
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    disponivel = models.BooleanField(default=True)
    registado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.preco}€"

class Pedido(models.Model):
    """Pedido criado pelo cliente"""
    STATUS_CHOICES = [
        ('aberto', 'Aberto - À espera de fornecedor'),
        ('em_negociacao', 'Em Negociação'),
        ('aceite', 'Aceite pelo fornecedor'),
        ('pago', 'Pago - Em Escrow'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('reembolsado', 'Reembolsado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    localizacao = models.CharField(max_length=255)
    coordenadas = models.JSONField(default=dict)
    orcamento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_limite = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    fornecedor_escolhido = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente.username} - {self.titulo}"

class Transacao(models.Model):
    """Transação entre cliente e fornecedor com escrow"""
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Pagamento'),
        ('pago', 'Pago - Em Escrow'),
        ('entregue', 'Entregue - Aguardando Confirmação'),
        ('confirmado', 'Confirmado - Pagamento Libertado'),
        ('reembolsado', 'Reembolsado'),
        ('cancelado', 'Cancelado'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='transacao')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    comissao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_fornecedor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    codigo_confirmacao = models.CharField(max_length=6, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_reembolso = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cliente.username} → {self.fornecedor.usuario.username} - {self.valor}€"

class Avaliacao(models.Model):
    """Avaliação do serviço pelo cliente"""
    transacao = models.OneToOneField(Transacao, on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transacao} - {self.nota}★"

class Notificacao(models.Model):
    """Notificações para utilizadores"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.mensagem[:50]}"