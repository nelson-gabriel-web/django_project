import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

# Apagar utilizadores antigos
User.objects.filter(username='joao').delete()
User.objects.filter(username='nelson').delete()

# Criar novo utilizador nelson
username = 'nelson'
password = 'Magn3t!cs'

user = User.objects.create_user(username=username, email='nelson@email.com', password=password)
PerfilUsuario.objects.create(usuario=user, tipo='cliente', nome_completo='Nelson Gabriel')

print('✅ Utilizador "nelson" criado com sucesso!')
print(f'   Username: {username}')
print(f'   Password: {password}')
print('   Email: nelson@email.com')