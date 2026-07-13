from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import RequisicaoCompra, Denuncia
from core.constantes import PALAVRAS_PROIBIDAS

class Command(BaseCommand):
    help = 'Moderação automática de produtos e denúncias'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('🔍 Iniciando moderação automática...')
        
        # 1. Verificar produtos com palavras proibidas
        produtos = RequisicaoCompra.objects.filter(status='pendente')
        produtos_removidos = 0
        
        for produto in produtos:
            texto = (produto.titulo + ' ' + produto.descricao).lower()
            for palavra in PALAVRAS_PROIBIDAS:
                if palavra.lower() in texto:
                    produto.status = 'cancelado'
                    produto.save()
                    produtos_removidos += 1
                    
                    # Criar denúncia automática
                    Denuncia.objects.create(
                        denunciante=None,  # Sistema
                        fornecedor=produto.cliente,
                        categoria='outros',
                        descricao=f'Removido automaticamente por conter palavra proibida: "{palavra}"',
                        status='aprovado'
                    )
                    break
        
        self.stdout.write(f'✅ {produtos_removidos} produtos removidos automaticamente')
        
        # 2. Denúncias antigas (mais de 7 dias)
        limite = timezone.now() - timedelta(days=7)
        denuncias_antigas = Denuncia.objects.filter(
            status='pendente',
            data_criacao__lte=limite
        )
        
        for denuncia in denuncias_antigas:
            denuncia.status = 'rejeitado'
            denuncia.data_resolucao = timezone.now()
            denuncia.save()
        
        self.stdout.write(f'✅ {denuncias_antigas.count()} denúncias antigas arquivadas')