from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        self.stdout.write("Reloading database")

        call_command('flush')
        call_command('clear_index', '--noinput')
        call_command('migrate')
        call_command('bootstrap')
        call_command('runserver')


