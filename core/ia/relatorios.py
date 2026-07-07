"""
Módulo para geração de relatórios automáticos
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from core.models import EventoSeguranca, ZonaRisco
from django.contrib.auth.models import User
import csv
from io import StringIO

class GeradorRelatorios:
    @staticmethod
    def gerar_relatorio_semanal(usuario):
        """Gera relatório semanal de segurança"""
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=7)
        
        eventos = EventoSeguranca.objects.filter(
            usuario=usuario,
            criado_em__gte=data_inicio,
            criado_em__lte=data_fim
        )
        
        zonas = ZonaRisco.objects.filter(usuario=usuario)
        
        relatorio = {
            'periodo': 'Semanal',
            'data_inicio': data_inicio.strftime('%d/%m/%Y'),
            'data_fim': data_fim.strftime('%d/%m/%Y'),
            'total_eventos': eventos.count(),
            'eventos_por_tipo': eventos.values('tipo').annotate(total=Count('id')),
            'zonas_risco': zonas.filter(nivel_risco__gte=3),
            'dias': [],
            'alertas_gerados': eventos.filter(alerta_enviado=True).count()
        }
        
        # Detalhes por dia
        for i in range(6, -1, -1):
            dia = data_fim - timedelta(days=i)
            eventos_dia = eventos.filter(criado_em__date=dia.date())
            relatorio['dias'].append({
                'data': dia.strftime('%d/%m/%Y'),
                'total': eventos_dia.count(),
                'eventos': eventos_dia[:5]
            })
        
        return relatorio

    @staticmethod
    def exportar_csv(usuario, dias=30):
        """Exporta eventos para CSV"""
        data_inicio = datetime.now() - timedelta(days=dias)
        eventos = EventoSeguranca.objects.filter(
            usuario=usuario,
            criado_em__gte=data_inicio
        ).order_by('-criado_em')
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Data', 'Tipo', 'Descrição', 'Local', 'Processado', 'Alertado'])
        
        # Dados
        for evento in eventos:
            writer.writerow([
                evento.criado_em.strftime('%d/%m/%Y %H:%M'),
                evento.get_tipo_display(),
                evento.descricao,
                evento.sensor.localizacao if evento.sensor else 'N/A',
                'Sim' if evento.processado else 'Não',
                'Sim' if evento.alerta_enviado else 'Não'
            ])
        
        return output.getvalue()

    @staticmethod
    def enviar_relatorio_semanal(usuario):
        """Envia relatório semanal por email"""
        relatorio = GeradorRelatorios.gerar_relatorio_semanal(usuario)
        
        html = render_to_string('core/relatorio_semanal.html', relatorio)
        texto = strip_tags(html)
        
        send_mail(
            subject=f"🔒 Relatório Semanal de Segurança - {usuario.username}",
            message=texto,
            from_email='relatorios@labsec.com',
            recipient_list=[usuario.email],
            html_message=html
        )
        
        return True