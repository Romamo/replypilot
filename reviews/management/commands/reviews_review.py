from django.core.management.base import BaseCommand

from reviews.models import Review


class Command(BaseCommand):
    help = 'Review and approve generated replies to upload'

    def handle(self, **options):
        qs = Review.objects.filter(state=Review.State.GENERATED, app__autoreview=True)
        qs.update(state=Review.State.READY)
