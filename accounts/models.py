from django.contrib.auth import get_user_model
from django.db import models


class Account(models.Model):
    class State(models.TextChoices):
        ACTIVE = 'ACTIVE'
        DISABLED = 'DISABLED'

    name = models.CharField(max_length=255)
    info = models.JSONField(verbose_name='Credentials JSON',
                            help_text='Insert contents of credentials json file. How to create https://support.appbot.co/help-docs/linking-your-google-play-account-to-appbot/')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    state = models.CharField(max_length=255, default=State.ACTIVE, choices=State.choices)
    signature = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
