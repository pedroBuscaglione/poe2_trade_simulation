from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Item

class Command(BaseCommand):
    help = 'Atribui um usuário como dono de todos os itens que ainda não têm dono.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome de usuário do dono padrão',
            required=True
        )

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Usuário '{username}' não encontrado."))
            return

        items = Item.objects.filter(owner__isnull=True)
        count = items.count()

        for item in items:
            item.owner = user
            item.save()

        self.stdout.write(self.style.SUCCESS(
            f'{count} itens atribuídos ao usuário "{username}".'
        ))
