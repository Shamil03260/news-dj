from django.core.management.base import BaseCommand
from news.scraper import fetch_news


class Command(BaseCommand):
    help = "Xəbərləri mənbədən toplayır"

    def handle(self, *args, **options):
        try:
            count = fetch_news()
            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} yeni xəbər əlavə edildi."
                )
            )
        except Exception as error:
            self.stderr.write(
                self.style.ERROR(f"Xəta: {error}")
            )