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
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    codigo_2fa = models.CharField(max_length=100, blank=True, null=True)
    ativo_2fa = models.BooleanField(default=False)
    codigos_recuperacao = models.JSONField(default=list, blank=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - 2FA: {'Ativo' if self.ativo_2fa else 'Inativo'}"