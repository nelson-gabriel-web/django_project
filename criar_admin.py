import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_site.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

print("🔄 Criando usuário admin...")

# Dados do admin
username = 'admin'
email = 'admin@nhonga.com'
password = 'admin123'

# Criar ou buscar usuário
user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f'✅ Usuário "{username}" criado com sucesso!')
    print(f'   Email: {email}')
    print(f'   Password: {password}')
else:
    print(f'ℹ️ Usuário "{username}" já existe.')

# Criar perfil para o admin
perfil, created = PerfilUsuario.objects.get_or_create(
    usuario=user,
    defaults={
        'tipo': 'admin',
        'nome_completo': 'Administrador',
        'status': 'ativo'
    }
)
print(f'✅ Perfil admin: {"criado" if created else "já existe"}')

print('\n✅ Script finalizado!')