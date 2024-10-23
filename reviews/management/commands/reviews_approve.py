from django.core.management.base import BaseCommand
from django.db import models

from accounts.models import Account
from apps.models import App
from reviews.models import Review


class Command(BaseCommand):
    help = 'Approve reviews to generate'

    def handle(self, **options):
        qs = Review.objects.filter(state=Review.State.NEW,
                                   app__autogenerate=True,
                                   app__state=App.State.ACTIVE,
                                   app__account__state=Account.State.ACTIVE,
                                   app__account__user__is_active=True) \
            .annotate(stars_min=models.F('app__stars_min')) \
            .filter(starRating__gte=models.F('stars_min'))
        qs.update(state=Review.State.APPROVED)
