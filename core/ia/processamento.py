"""
Módulo de Inteligência Artificial para Processamento de Eventos
"""
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from core.models import EventoSeguranca, ZonaRisco

# ============================================
# DETEÇÃO DE MOVIMENTO
# ============================================

class DetectorMovimento:
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.contador = 0
    
    def detectar(self, frame):
        """Detecta movimento em um frame"""
        fgmask = self.fgbg.apply(frame)
        fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)[1]
        fgmask = cv2.erode(fgmask, None, iterations=2)
        fgmask = cv2.dilate(fgmask, None, iterations=2)
        
        contornos, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        movimento_detectado = False
        for contorno in contornos:
            if cv2.contourArea(contorno) > 500:
                movimento_detectado = True
                break
        
        return movimento_detectado, fgmask

# ============================================
# ANÁLISE DE COMPORTAMENTO SUSPEITO
# ============================================

def analisar_comportamento(evento):
    """Analisa se o evento pode ser considerado suspeito"""
    # Critérios simples
    criterios = []
    
    # Horário (eventos noturnos são mais suspeitos)
    hora = evento.criado_em.hour
    if hora < 6 or hora > 20:
        criterios.append('Horário noturno')
    
    # Frequência (muitos eventos em pouco tempo)
    eventos_recentes = EventoSeguranca.objects.filter(
        sensor=evento.sensor,
        criado_em__gte=evento.criado_em - timedelta(minutes=5)
    ).count()
    
    if eventos_recentes > 3:
        criterios.append('Alta frequência de eventos')
    
    # Atualizar zona de risco
    if evento.sensor:
        zona, _ = ZonaRisco.objects.get_or_create(
            nome=f"Zona {evento.sensor.localizacao}",
            defaults={'localizacao': evento.sensor.localizacao}
        )
        zona.eventos += 1
        zona.ultimo_evento = evento.criado_em
        
        # Aumentar nível de risco se houver muitos eventos
        if zona.eventos > 10:
            zona.nivel_risco = min(4, zona.nivel_risco + 1)
        zona.save()
    
    return {
        'suspeito': len(criterios) > 1,
        'criterios': criterios,
        'nivel_risco': len(criterios)
    }

# ============================================
# PREDIÇÃO DE ZONAS DE RISCO
# ============================================

def predizer_zonas_risco():
    """Prediz quais zonas têm maior probabilidade de crime"""
    zonas = ZonaRisco.objects.all()
    
    for zona in zonas:
        # Fator tempo (zonas com eventos recentes)
        if zona.ultimo_evento:
            dias_desde_ultimo = (datetime.now() - zona.ultimo_evento).days
            if dias_desde_ultimo < 7:
                zona.nivel_risco = min(4, zona.nivel_risco + 1)
            elif dias_desde_ultimo > 30:
                zona.nivel_risco = max(1, zona.nivel_risco - 1)
        
        # Fator quantidade de eventos
        if zona.eventos > 20:
            zona.nivel_risco = min(4, zona.nivel_risco + 1)
        
        zona.save()
    
    return zonas

# ============================================
# PROCESSAMENTO PRINCIPAL
# ============================================

def processar_evento_ia(evento):
    """Função principal que processa um evento com IA"""
    from django.utils.timezone import timedelta
    
    # 1. Analisar comportamento
    analise = analisar_comportamento(evento)
    
    # 2. Se for suspeito, marcar e enviar alerta
    if analise['suspeito']:
        evento.descricao = f"⚠️ COMPORTAMENTO SUSPEITO: {', '.join(analise['criterios'])}"
        evento.save()
        
        # Enviar alerta
        from .notificacoes import enviar_alerta
        enviar_alerta(evento)
    
    # 3. Atualizar processado
    evento.processado = True
    evento.save()
    
    return analise