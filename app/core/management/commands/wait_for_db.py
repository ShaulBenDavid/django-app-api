"""""
 Django command to wait for db to be available
"""""
import time

from django.db import connections
from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                # the  above  check was not enough, github actions raised
                # an error that the databse was not redy yet
                # this is why we adding extra check
                # Try to establish a connection by executing a test query
                connections['default'].cursor().execute('SELECT 1')
                db_up = True  # if the check is succeesful
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
