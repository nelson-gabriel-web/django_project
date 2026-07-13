import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

print("🔧 A resetar utilizadores...")

# Apagar TODOS os utilizadores (cuidado!)
User.objects.all().delete()
print("✅ Todos os utilizadores removidos!")

# Criar novo utilizador pressagio
print("\n🔧 A criar utilizador pressagio...")
user = User.objects.create_user(
    username='pressagio',
    email='pressagioone@gmail.com',
    password='pressagio123'
)

PerfilUsuario.objects.create(
    usuario=user,
    tipo='cliente',
    nome_completo='Pressagio One'
)

print('\n✅ Utilizador "pressagio" criado com sucesso!')
print('   Username: pressagio')
print('   Password: pressagio123')
print('   Email: pressagioone@gmail.com')

# Listar todos os utilizadores
print('\n📋 Utilizadores existentes:')
for u in User.objects.all():
    print(f'   - {u.username} (email: {u.email})')