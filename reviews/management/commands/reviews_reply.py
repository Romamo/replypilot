from django.core.management.base import BaseCommand
from django.utils import timezone


from accounts.models import Account
from apps.models import App
from reviews.models import Review
from reviews.services.exceptions import ReplyTooLong, ReviewNotFound
from reviews.services.publisher import AndroidPublisherService


class Command(BaseCommand):
    help = 'Reply'

    def handle(self, **options):
        qs = Account.objects.filter(state=Account.State.ACTIVE)
        for account in qs:
            publisher = AndroidPublisherService(account.info)
            for app in account.app_set.filter(state=App.State.ACTIVE):
                for review in app.review_set.filter(state=Review.State.READY):
                    if review.reply and len(review.reply) > 350:
                        review.reason = 'Too long'
                        review.state = Review.State.ERROR
                        review.save(update_fields=['state', 'reason'])
                        continue

                    try:
                        response = publisher.reply(app.packageName, review.uuid, review.reply)
                    except ReplyTooLong as e:
                        review.reason = str(e)
                        review.state = Review.State.ERROR
                        review.save(update_fields=['state', 'reason'])
                        continue
                    except ReviewNotFound as e:
                        review.reason = str(e)
                        review.state = Review.State.ERROR
                        review.save(update_fields=['state', 'reason'])
                        continue

                    if response:
                        review.state = Review.State.COMPLETE
                        review.replied = timezone.now()
                        review.save(update_fields=['state', 'replied'])
                    else:
                        review.reason = 'Unknown error'
                        review.state = Review.State.ERROR
                        review.save(update_fields=['state', 'reason'])

    # def add_arguments(self, parser):
    #     parser.add_argument('--init',
    #                         action='store_true',
    #                         dest='init',
    #                         default=None,
    #                         help='init')
