from django.core.management.base import BaseCommand

from api_integration.exchange_rate import get_stored_history


class Command(BaseCommand):
    help = "Show stored exchange rate data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Max number of records to show (default: 20)',
        )

    def handle(self, *args, **options):
        limit = min(max(options['limit'], 1), 200)
        try:
            rows = get_stored_history(limit=limit)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Database error: {e}'))
            return
        if not rows:
            self.stdout.write('No stored data yet. Call /api/get_exchange_rate/ first.')
            return
        self.stdout.write(self.style.SUCCESS(f'Stored exchange rate data (last {len(rows)}):'))
        self.stdout.write('')
        for r in rows:
            self.stdout.write(f"  id={r['id']}  timestamp={r['timestamp']}  rate={r['exchange_rate']}  status={r['status_code']}")
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total shown: {len(rows)}'))
