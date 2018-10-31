import os
from django.core.management import call_command
from django.core.management.commands import runserver


class Command(runserver.Command):

    def handle(self, *args, **options):
        """
        Reload the database by emptying, re populating and then running the server
        """
        # Catch an issue where runserver spawns multiple threads and runs this command twice.
        if not os.environ.get('RUN_MAIN', False):
            self.stdout.write("Reloading database")
            call_command('flush', '--noinput')
            call_command('clear_index', '--noinput')
            call_command('migrate')
            call_command('bootstrap')

        super().handle(*args, **options)
