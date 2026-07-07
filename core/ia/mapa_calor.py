"""
Módulo para geração de mapa de calor de eventos
"""
import json
from datetime import datetime, timedelta
from django.db.models import Count
from core.models import EventoSeguranca

class MapaCalor:
    @staticmethod
    def gerar_dados_mapa(usuario, dias=7):
        """Gera dados para mapa de calor dos últimos N dias"""
        data_inicio = datetime.now() - timedelta(days=dias)
        
        eventos = EventoSeguranca.objects.filter(
            usuario=usuario,
            criado_em__gte=data_inicio
        ).values('criado_em__date').annotate(
            total=Count('id')
        ).order_by('criado_em__date')
        
        dados = []
        for evento in eventos:
            dados.append({
                'data': evento['criado_em__date'].strftime('%Y-%m-%d'),
                'total': evento['total']
            })
        
        return dados

    @staticmethod
    def gerar_dados_por_hora(usuario, dias=7):
        """Gera dados por hora do dia"""
        data_inicio = datetime.now() - timedelta(days=dias)
        
        eventos = EventoSeguranca.objects.filter(
            usuario=usuario,
            criado_em__gte=data_inicio
        ).extra(
            select={'hora': "strftime('%H', criado_em)"}
        ).values('hora').annotate(
            total=Count('id')
        ).order_by('hora')
        
        dados = {str(i): 0 for i in range(24)}
        for evento in eventos:
            dados[evento['hora']] = evento['total']
        
        return dados

    @staticmethod
    def gerar_heatmap_completo(usuario, dias=30):
        """Gera mapa de calor completo"""
        return {
            'diario': MapaCalor.gerar_dados_mapa(usuario, dias),
            'por_hora': MapaCalor.gerar_dados_por_hora(usuario, dias),
            'dias': dias
        }