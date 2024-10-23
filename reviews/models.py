from django.contrib.auth import get_user_model
from django.db import models

from apps.models import App


class Review(models.Model):
    class State(models.TextChoices):
        """
        import -> NEW
        NEW -> (auto)approve -> APPROVED
        APPROVED -> generate -> GENERATED
        GENERATED -> (auto)review -> READY
        READY -> reply -> COMPLETE
        """
        NEW = 'NEW'
        APPROVED = 'APPROVED'
        GENERATED = 'GENERATED'
        READY = 'READY'
        COMPLETE = 'COMPLETE'
        ERROR = 'ERROR'

    author = models.CharField(max_length=255)
    starRating = models.PositiveSmallIntegerField()
    thumbsUpCount = models.PositiveSmallIntegerField(default=0)
    thumbsDownCount = models.PositiveSmallIntegerField(default=0)
    text = models.TextField()
    originalText = models.TextField()
    reply = models.TextField()
    replied = models.DateTimeField(default=None, null=True, blank=True)

    starRatingChanged = models.PositiveSmallIntegerField(default=0)
    textChanged = models.TextField()
    lastModifiedChanged = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Changed')

    lastModified = models.DateTimeField(verbose_name='Modified')

    uuid = models.UUIDField(unique=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    reviewerLanguage = models.CharField(max_length=7, verbose_name='Language')
    device = models.CharField(max_length=255)
    androidOsVersion = models.PositiveSmallIntegerField()
    appVersionCode = models.PositiveSmallIntegerField()
    appVersionName = models.CharField(max_length=255)

    state = models.CharField(max_length=255, default=State.NEW, choices=State.choices)
    reason = models.CharField(max_length=255, default='')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    cost = models.PositiveIntegerField(default=0)  # * 1000000

    # country = models.CharField(max_length=255, default='')
    # pos = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.uuid)
