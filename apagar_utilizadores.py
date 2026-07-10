import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

print("🔧 A apagar todos os utilizadores...")

# Contar quantos utilizadores existem
total = User.objects.count()
print(f"📋 Utilizadores encontrados: {total}")

if total > 0:
    # Apagar perfis primeiro (por causa da relação)
    PerfilUsuario.objects.all().delete()
    print("✅ Perfis apagados")
    
    # Apagar utilizadores
    User.objects.all().delete()
    print("✅ Utilizadores apagados")
    
    print(f"✅ {total} utilizadores removidos!")
else:
    print("ℹ️ Nenhum utilizador para apagar.")

# Verificar
print(f"\n📋 Utilizadores restantes: {User.objects.count()}")