import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

print("🔧 A criar utilizador...")

username = 'joao'
password = 'joao123'
email = 'joao@email.com'

# Criar utilizador
user = User.objects.create_user(
    username=username,
    email=email,
    password=password
)

# Criar perfil
PerfilUsuario.objects.create(
    usuario=user,
    tipo='cliente',
    nome_completo='João Silva',
    status='ativo'
)

print(f'✅ Utilizador "{username}" criado!')
print(f'   Email: {email}')
print(f'   Password: {password}')

print("\n📋 Utilizadores existentes:")
for u in User.objects.all():
    print(f'   - {u.username}')