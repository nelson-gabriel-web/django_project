"""
Módulo de Notificações - Telegram / Email / SMS
"""
import requests
from django.core.mail import send_mail
from django.conf import settings
from core.models import Alerta
from webpush import send_user_notification
from django.contrib.auth.models import User

# ============================================
# TELEGRAM
# ============================================

def enviar_telegram(mensagem):
    """Envia mensagem via Telegram Bot"""
    try:
        bot_token = "SEU_BOT_TOKEN_AQUI"  # Criar no @BotFather
        chat_id = "SEU_CHAT_ID_AQUI"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': mensagem,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# ============================================
# EMAIL
# ============================================

def enviar_email(alerta):
    """Envia alerta por email"""
    try:
        send_mail(
            subject=f"🔒 Alerta de Segurança - {alerta.evento.get_tipo_display()}",
            message=alerta.mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ALERT_EMAIL],
            fail_silently=False,
        )
        return True
    except:
        return False

# ============================================
# ALERTA PRINCIPAL
# ============================================

def enviar_alerta(evento):
    """Envia alerta por todos os canais configurados"""
    mensagem = f"""
🔒 <b>ALERTA DE SEGURANÇA</b>

📌 <b>Tipo:</b> {evento.get_tipo_display()}
📍 <b>Local:</b> {evento.sensor.localizacao if evento.sensor else 'Desconhecido'}
🕐 <b>Hora:</b> {evento.criado_em.strftime('%d/%m/%Y %H:%M:%S')}
📝 <b>Descrição:</b> {evento.descricao}
    """
    
    # Telegram
    if enviar_telegram(mensagem):
        Alerta.objects.create(
            evento=evento,
            tipo='telegram',
            mensagem=mensagem,
            lido=False
        )
    
    # Email
    if enviar_email(mensagem):
        Alerta.objects.create(
            evento=evento,
            tipo='email',
            mensagem=mensagem,
            lido=False
        )

def enviar_push_notification(user, titulo, mensagem, url='/'):
    """Envia notificação push para o telemóvel do utilizador"""
    try:
        payload = {
            'head': titulo,
            'body': mensagem,
            'icon': 'https://labsec.com/icon.png',
            'url': url,
            'requireInteraction': True,
            'tag': 'alerta',
            'actions': [
                {'action': 'ver', 'title': 'Ver detalhes'},
                {'action': 'ignorar', 'title': 'Ignorar'}
            ]
        }
        send_user_notification(user=user, payload=payload, ttl=1000)
        return True
    except Exception as e:
        print(f"Erro push: {e}")
        return False