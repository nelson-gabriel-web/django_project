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
