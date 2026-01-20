from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates admin user with default credentials'

    def handle(self, *args, **options):
        username = 'admin'
        password = '1database'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
            # Update password in case it changed
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated password for user "{username}"'))
        else:
            User.objects.create_superuser(
                username=username,
                email='admin@example.com',
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))
