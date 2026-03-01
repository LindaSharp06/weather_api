from django.core.management.base import BaseCommand

from api_integration.exchange_rate import _get_engine


class Command(BaseCommand):
    help = 'Create the requests and responses tables in PostgreSQL (SQLAlchemy)'

    def handle(self, *args, **options):
        try:
            engine = _get_engine()
            self.stdout.write(self.style.SUCCESS('Tables "requests" and "responses" created (or already exist).'))
        except Exception as e:
            self.stderr.write(self.style.ERROR('Failed to create tables: %s' % e))
            raise
