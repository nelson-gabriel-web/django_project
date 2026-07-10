import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

# Verificar se o admin já existe
admin_exists = User.objects.filter(username='admin').exists()
print(f'Admin existe: {admin_exists}')

# Criar admin se não existir
if not admin_exists:
    user = User.objects.create_user(
        username='admin',
        email='admin@nhonga.com',
        password='admin123'
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    # Criar perfil
    PerfilUsuario.objects.create(
        usuario=user,
        tipo='admin',
        nome_completo='Administrador',
        status='ativo'
    )
    print('✅ Admin criado com sucesso!')
else:
    print('ℹ️ Admin já existe')

# Listar todos os utilizadores
print('\n📋 Utilizadores existentes:')
for u in User.objects.all():
    print(f'   - {u.username} (email: {u.email})')