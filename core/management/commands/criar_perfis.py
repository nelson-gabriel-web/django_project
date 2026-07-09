from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Cria perfis para todos os utilizadores que não têm perfil'

    def handle(self, *args, **options):
        users = User.objects.all()
        self.stdout.write(f'Total de utilizadores: {users.count()}')

        criados = 0
        existentes = 0

        for user in users:
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            if created:
                criados += 1
                self.stdout.write(self.style.SUCCESS(f'Perfil criado para {user.username}'))
            else:
                existentes += 1
                self.stdout.write(self.style.WARNING(f'Perfil já existe para {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {criados} perfis criados'))
        self.stdout.write(self.style.SUCCESS(f'⚠️ {existentes} perfis já existiam'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total: {PerfilUsuario.objects.count()} perfis'))