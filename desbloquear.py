import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TentativaLogin

username = 'joao'

try:
    user = User.objects.get(username=username)
    tentativa, created = TentativaLogin.objects.get_or_create(usuario=user)
    tentativa.tentativas = 0
    tentativa.bloqueado = False
    tentativa.save()
    print(f'✅ Conta "{username}" desbloqueada!')
    print(f'   Tentativas: {tentativa.tentativas}')
    print(f'   Bloqueado: {tentativa.bloqueado}')
except User.DoesNotExist:
    print(f'❌ Utilizador "{username}" não encontrado.')