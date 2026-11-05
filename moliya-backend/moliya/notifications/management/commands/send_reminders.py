from django.core.management.base import BaseCommand

from moliya.notifications.container import send_reminders


class Command(BaseCommand):
    help = "Sinov va obuna tugashi haqida eslatmalarni yuboradi. Kuniga bir marta cron orqali ishga tushiring."

    def handle(self, *args, **options):
        result = send_reminders().execute()
        self.stdout.write(self.style.SUCCESS(f"Tekshirildi: {result['checked']}, yuborildi: {result['sent']}"))
