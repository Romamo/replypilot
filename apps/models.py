import random

from django.db import models

from accounts.models import Account


class App(models.Model):
    class State(models.TextChoices):
        ACTIVE = 'ACTIVE'
        DISABLED = 'DISABLED'

    url = models.URLField()
    packageName = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    keywords = models.TextField(help_text='Keywords to promote. One per line', blank=True)

    state = models.CharField(max_length=255, default=State.ACTIVE, choices=State.choices)

    autogenerate = models.BooleanField(default=True, help_text='Instantly generate replies for all reviews')
    autoreview = models.BooleanField(default=True, help_text='Automatically approve and submit replies')
    num_reviews = models.PositiveSmallIntegerField(default=10, help_text='Number of last reviews to download')

    harvest = models.BooleanField(default=True,
                                  help_text='One time action: Harvest pinned reviews from app page for each language')

    classify = models.BooleanField(default=False,
                                   help_text='Classify reviews longer than 100 characters by sentiment and topic')
    limit_replies = models.PositiveSmallIntegerField(default=10, help_text='Limit number of replies per day')
    stars_min = models.PositiveSmallIntegerField(default=0, help_text='Minimum stars to reply(>=)')

    # imported = models.DateTimeField(default=None, null=True, blank=True)
    # replied = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return self.name or self.packageName

    def get_keyword(self):
        return random.choice(self.keywords.replace("\r","").strip().split("\n"))
