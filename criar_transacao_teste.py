# criar_transacao_teste.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Transacao, PerfilUsuario
from decimal import Decimal

def criar_transacao_teste():
    # Procurar ou criar cliente
    cliente = User.objects.filter(username='cliente').first()
    if not cliente:
        cliente = User.objects.create_user('cliente', 'cliente@teste.com', 'cliente123')
        PerfilUsuario.objects.create(usuario=cliente, tipo='cliente')
        print('👤 Cliente criado: cliente / senha: cliente123')

    # Procurar ou criar fornecedor
    fornecedor = User.objects.filter(username='fornecedor').first()
    if not fornecedor:
        fornecedor = User.objects.create_user('fornecedor', 'fornecedor@teste.com', 'fornecedor123')
        PerfilUsuario.objects.create(usuario=fornecedor, tipo='fornecedor')
        print('🏢 Fornecedor criado: fornecedor / senha: fornecedor123')

    # Criar transação
    transacao = Transacao.objects.create(
        cliente=cliente,
        fornecedor=fornecedor,
        titulo='Teste Pagamento VISA',
        descricao='Pagamento de teste com cartão VISA - Nhonga',
        valor_total=Decimal('100.00'),
        status='pendente'
    )

    print('=' * 60)
    print('✅ TRANSAÇÃO CRIADA COM SUCESSO!')
    print('=' * 60)
    print(f'📋 ID da Transação: {transacao.id}')
    print(f'👤 Cliente: {cliente.username} (senha: cliente123)')
    print(f'🏢 Fornecedor: {fornecedor.username} (senha: fornecedor123)')
    print(f'💰 Valor: $100.00 USD')
    print('-' * 60)
    print('🔗 ACESSE ESTA URL PARA TESTAR:')
    print(f'   http://127.0.0.1:8000/pagamento/visa/{transacao.id}/')
    print('-' * 60)
    print('💳 CARTÃO DE TESTE: 4242 4242 4242 4242')
    print('📅 Data: 12/28')
    print('🔐 CVC: 123')
    print('=' * 60)

if __name__ == '__main__':
    criar_transacao_teste()