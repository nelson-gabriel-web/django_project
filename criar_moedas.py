import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_site.settings')
django.setup()

from core.models import Moeda

print("🔄 Criando moedas...")

# Criar Metical (moeda base)
mzn, created = Moeda.objects.get_or_create(
    codigo='MZN',
    defaults={
        'nome': 'Metical',
        'simbolo': 'MT',
        'taxa_cambio': 1.0000,
        'ativa': True,
        'padrao': True
    }
)
print(f'✅ Metical: {"criado" if created else "já existe"}')

# Criar Dólar Americano
usd, created = Moeda.objects.get_or_create(
    codigo='USD',
    defaults={
        'nome': 'Dólar Americano',
        'simbolo': '$',
        'taxa_cambio': 0.0016,
        'ativa': True,
        'padrao': False
    }
)
print(f'✅ Dólar: {"criado" if created else "já existe"}')

# Criar Euro
eur, created = Moeda.objects.get_or_create(
    codigo='EUR',
    defaults={
        'nome': 'Euro',
        'simbolo': '€',
        'taxa_cambio': 0.0015,
        'ativa': True,
        'padrao': False
    }
)
print(f'✅ Euro: {"criado" if created else "já existe"}')

# Listar todas as moedas
print('\n📋 Moedas disponíveis:')
for m in Moeda.objects.all():
    print(f'   - {m.codigo}: {m.nome} ({m.simbolo}) - Taxa: {m.taxa_cambio}')

print('\n✅ Script finalizado!')