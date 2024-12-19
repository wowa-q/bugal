"""
Kann wiefolgt ausgeführt wereden: uv run python manage.py checkstatic
"""
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check STATIC settings"

    def handle(self, *args, **kwargs):
        self.stdout.write("STATIC_URL: {}".format(settings.STATIC_URL))
        self.stdout.write("STATIC_ROOT: {}".format(settings.STATIC_ROOT))
        self.stdout.write("STATICFILES_DIRS: {}".format(settings.STATICFILES_DIRS))

        self.stdout.write("TEMPLATES_DIR: {}".format(settings.TEMPLATES_DIR))
        self.stdout.write("BASE_DIR: {}".format(settings.BASE_DIR))
        