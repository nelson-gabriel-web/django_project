import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

# Criar utilizador joao
if not User.objects.filter(username='joao').exists():
    user = User.objects.create_user(username='joao', email='joao@email.com', password='joao123')
    PerfilUsuario.objects.create(usuario=user, tipo='cliente', nome_completo='João Silva')
    print('✅ Utilizador joao criado!')
else:
    print('ℹ️ Utilizador joao já existe')

# Verificar colunas
print('Colunas do PerfilUsuario:', [f.name for f in PerfilUsuario._meta.fields])