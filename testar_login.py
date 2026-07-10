import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth import authenticate

print("🔧 A testar login...")

username = 'joao'
password = 'joao123'

user = authenticate(username=username, password=password)

if user is not None:
    print(f'✅ Login funcionou para: {username}')
else:
    print(f'❌ Login falhou para: {username}')