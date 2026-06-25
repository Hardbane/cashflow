import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Создаёт суперпользователя из переменных окружения, если он ещё не существует.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write('Переменные DJANGO_SUPERUSER_USERNAME/PASSWORD не заданы, суперпользователь не создан.')
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True})
        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь {username} создан.'))
            return

        changed = False
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            changed = True
        if email and user.email != email:
            user.email = email
            changed = True
        if changed:
            user.save()
        self.stdout.write(f'Суперпользователь {username} уже существует.')
