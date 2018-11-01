from subprocess import call

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a fresh sqllite database'

    def handle(self, *args, **options):
        target_db = settings.DATABASES.get("default")
        db_name = target_db.get('NAME')
        #bkup_db_name = "{}.empty".format(db_name)

        call(["rm", db_name])
        #call_command('syncdb')
        #call(["cp", bkup_db_name, db_name])
