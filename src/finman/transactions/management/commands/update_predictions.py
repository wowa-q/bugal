from django.core.management.base import BaseCommand

from transactions.services.prediction import update_predictions


class Command(BaseCommand):
    help = 'Update payment predictions based on transaction history'

    def handle(self, *args, **options):
        self.stdout.write('Updating predictions...')
        update_predictions()
        self.stdout.write(self.style.SUCCESS('Predictions updated successfully.'))
