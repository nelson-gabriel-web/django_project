import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_site.settings')
django.setup()

from core.models import Categoria

print("🔄 Criando categorias...")

categorias = [
    {'nome': 'Veículos', 'icone': '🚗', 'descricao': 'Carros, motos, bicicletas e acessórios'},
    {'nome': 'Eletrônicos', 'icone': '📱', 'descricao': 'Smartphones, computadores, TVs e gadgets'},
    {'nome': 'Imóveis', 'icone': '🏠', 'descricao': 'Casas, apartamentos, terrenos e comércio'},
    {'nome': 'Alimentação', 'icone': '🍕', 'descricao': 'Comidas, bebidas e produtos alimentícios'},
    {'nome': 'Roupas', 'icone': '👕', 'descricao': 'Vestuário, calçados e acessórios'},
    {'nome': 'Serviços', 'icone': '🔧', 'descricao': 'Serviços profissionais e mão de obra'},
    {'nome': 'Saúde', 'icone': '🏥', 'descricao': 'Produtos e serviços de saúde'},
    {'nome': 'Educação', 'icone': '📚', 'descricao': 'Cursos, livros e materiais educativos'},
]

for cat in categorias:
    obj, created = Categoria.objects.get_or_create(
        nome=cat['nome'],
        defaults={
            'icone': cat['icone'],
            'descricao': cat['descricao'],
            'ativo': True
        }
    )
    print(f'✅ {cat["nome"]}: {"criado" if created else "já existe"}')

print('\n📋 Categorias disponíveis:')
for c in Categoria.objects.filter(ativo=True):
    print(f'   - {c.icone} {c.nome}')

print('\n✅ Script finalizado!')