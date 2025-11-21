# app/management/commands/prune_auditlogs.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from audit.models import AuditLog
from datetime import timedelta

class Command(BaseCommand):
    help = "Prune AuditLog older than N days"
    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options["days"])
        qs = AuditLog.objects.filter(timestamp__lt=cutoff)
        count = qs.count()
        qs.delete()
        self.stdout.write(f"Deleted {count} logs older than {options['days']} days")
