import os
import sys
import django

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura o settings - USANDO django_project (nome da sua pasta)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

# Inicializa o Django
django.setup()

from django.contrib.auth.models import User
from core.models import Moeda, Categoria, PerfilUsuario

print("=" * 50)
print("🚀 CONFIGURAÇÃO INICIAL DA PLATAFORMA NHONGA")
print("=" * 50)

# 1. Criar Moedas
print("\n📊 1. CRIANDO MOEDAS...")
moedas = [
    {'codigo': 'MZN', 'nome': 'Metical', 'simbolo': 'MT', 'taxa': 1.0000, 'padrao': True},
    {'codigo': 'USD', 'nome': 'Dólar Americano', 'simbolo': '$', 'taxa': 0.0016, 'padrao': False},
    {'codigo': 'EUR', 'nome': 'Euro', 'simbolo': '€', 'taxa': 0.0015, 'padrao': False},
]

for dados in moedas:
    obj, created = Moeda.objects.get_or_create(
        codigo=dados['codigo'],
        defaults={
            'nome': dados['nome'],
            'simbolo': dados['simbolo'],
            'taxa_cambio': dados['taxa'],
            'ativa': True,
            'padrao': dados['padrao']
        }
    )
    print(f'   ✅ {dados["codigo"]}: {"criado" if created else "já existe"}')

# 2. Criar Categorias
print("\n📂 2. CRIANDO CATEGORIAS...")
categorias = [
    {'nome': 'Veículos', 'icone': '🚗'},
    {'nome': 'Eletrônicos', 'icone': '📱'},
    {'nome': 'Imóveis', 'icone': '🏠'},
    {'nome': 'Alimentação', 'icone': '🍕'},
    {'nome': 'Roupas', 'icone': '👕'},
    {'nome': 'Serviços', 'icone': '🔧'},
]

for cat in categorias:
    obj, created = Categoria.objects.get_or_create(
        nome=cat['nome'],
        defaults={'icone': cat['icone'], 'ativo': True}
    )
    print(f'   ✅ {cat["nome"]}: {"criado" if created else "já existe"}')

# 3. Criar Admin
print("\n👤 3. CRIANDO ADMIN...")
username = 'admin'
email = 'admin@nhonga.com'
password = 'admin123'

user, created = User.objects.get_or_create(
    username=username,
    defaults={'email': email, 'is_staff': True, 'is_superuser': True}
)

if created:
    user.set_password(password)
    user.save()
    print(f'   ✅ Admin criado!')
    print(f'   👤 Username: {username}')
    print(f'   📧 Email: {email}')
    print(f'   🔑 Password: {password}')
else:
    print(f'   ℹ️ Admin já existe')

perfil, created = PerfilUsuario.objects.get_or_create(
    usuario=user,
    defaults={'tipo': 'admin', 'nome_completo': 'Administrador', 'status': 'ativo'}
)
print(f'   ✅ Perfil admin: {"criado" if created else "já existe"}')

# 4. Resumo Final
print("\n" + "=" * 50)
print("✅ CONFIGURAÇÃO COMPLETA!")
print("=" * 50)

print("\n📊 MOEDAS DISPONÍVEIS:")
for m in Moeda.objects.filter(ativa=True):
    print(f'   {m.simbolo} {m.codigo} - {m.nome} (Taxa: {m.taxa_cambio})')

print("\n📂 CATEGORIAS:")
for c in Categoria.objects.filter(ativo=True):
    print(f'   {c.icone} {c.nome}')

print("\n👤 LOGIN ADMIN:")
print(f'   Username: admin')
print(f'   Password: admin123')

print("\n🚀 Pronto para usar! Execute: python manage.py runserver")
print("=" * 50)