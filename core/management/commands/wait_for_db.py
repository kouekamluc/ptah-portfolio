import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django management command to pause execution until the database is available."""

    help = "Waits for database connection to be established before executing migrations or starting application."

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Maximum seconds to wait for database connection (default: 30)",
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=1.0,
            help="Seconds to wait between retry attempts (default: 1.0)",
        )

    def handle(self, *args, **options):
        timeout = options["timeout"]
        interval = options["interval"]
        self.stdout.write(self.style.NOTICE(f"Checking database connection (timeout: {timeout}s)..."))

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                db_conn = connections["default"]
                with db_conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Database connection established successfully ({db_conn.vendor}: {db_conn.settings_dict.get('NAME')})!"
                    )
                )
                return
            except OperationalError as e:
                self.stdout.write(
                    self.style.WARNING(f"Database unavailable ({e}), retrying in {interval}s...")
                )
                time.sleep(interval)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Waiting for database connection ({e}), retrying in {interval}s...")
                )
                time.sleep(interval)

        self.stderr.write(self.style.ERROR(f"Database connection timed out after {timeout} seconds."))
        raise SystemExit(1)
