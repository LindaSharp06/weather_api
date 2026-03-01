from django.core.management.base import BaseCommand

from api_integration.exchange_rate import fetch_and_store_data, _run_fetcher_loop


class Command(BaseCommand):
    help = "Fetch exchange rate and store in DB. Use --loop to run every N minutes (or --interval-sec for seconds)."

    def add_arguments(self, parser):
        parser.add_argument("--loop", action="store_true", help="Run every N minutes until Ctrl+C")
        parser.add_argument("--interval", type=int, default=5, help="Minutes between fetches when using --loop")
        parser.add_argument("--interval-sec", type=int, default=None, help="Seconds between fetches (overrides --interval)")

    def handle(self, *args, **options):
        if not options["loop"]:
            fetch_and_store_data()
            self.stdout.write(self.style.SUCCESS("Fetched and stored."))
            return
        sec = options.get("interval_sec")
        if sec is not None:
            sec = max(10, min(sec, 86400))
            self.stdout.write("Fetching every %s second(s). Ctrl+C to stop." % sec)
            kwargs = {"interval_seconds": sec}
        else:
            n = max(1, min(options["interval"], 1440))
            self.stdout.write("Fetching every %s minute(s). Ctrl+C to stop." % n)
            kwargs = {"interval_minutes": n}
        try:
            _run_fetcher_loop(**kwargs)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopped."))