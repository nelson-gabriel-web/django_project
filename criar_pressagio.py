import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

# Apagar utilizadores antigos
User.objects.filter(username='joao').delete()
User.objects.filter(username='nelson').delete()
User.objects.filter(username='pressagio').delete()

# Criar novo utilizador
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

print('✅ Utilizador "pressagio" criado com sucesso!')
print('   Username: pressagio')
print('   Password: pressagio123')
print('   Email: pressagioone@gmail.com')

# Listar todos os utilizadores
print('\n📋 Todos os utilizadores:')
for u in User.objects.all():
    print(f'   - {u.username}')