from django.core.management.base import BaseCommand
from usermgmt import models


class Command(BaseCommand):
    help = 'Reserves a username by creating a dummy user with it set, for use by the auth-server'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']
        if models.CustomUser.objects.create_user(username):
            self.stdout.write(self.style.SUCCESS(f'Successfully registered username {username}'))