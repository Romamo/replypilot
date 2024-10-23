import openai
from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Review
from reviews.services.exceptions import RateLimitError
from reviews.services.generator import ReplyGenerator

openai.api_key = settings.OPENAI_API_KEY


class Command(BaseCommand):
    help = 'Generate replies'

    def handle(self, **options):
        limit_apps = {}
        if options['reviewid']:
            qs = Review.objects.filter(uuid=options['reviewid'])
        else:
            qs = Review.objects.filter(state=Review.State.APPROVED)
        reply_generator = ReplyGenerator()
        is_limit_reached = False
        for review in qs.order_by('-lastModified'):
            if review.app_id not in limit_apps:
                limit_apps[review.app_id] = 1
            else:
                break
            print(review)
            if is_limit_reached:
                review.state = Review.State.ERROR
                review.reason = 'RateLimitError'
                review.save(update_fields=['reason', 'state'])
                continue

            try:
                text, cost = reply_generator.generate_reply(text=review.originalText or review.text,
                                                            lang=review.reviewerLanguage,
                                                            starRating=review.starRating,
                                                            authorName=review.author,
                                                            keyword=review.app.get_keyword(),
                                                            signature=review.app.account.signature)
            except RateLimitError:
                review.state = Review.State.ERROR
                review.reason = 'RateLimitError'
                review.save(update_fields=['reason', 'state'])
                is_limit_reached = True
                break

            if text:
                review.cost += int(cost * 1000000)
                review.save(update_fields=['cost'])

                if len(text) > 350:
                    print(f"Generated text length {len(text)}")
                    continue
                if text.find('[') > 0:
                    print(f"Generated text with [: {text}")
                    continue
                if text.find('@') > 0:
                    print(f"Generated text with @: {text}")
                    continue
                if text.find('https://') > 0:
                    print(f"Generated text with https: {text}")
                    continue
                review.reply = text
                review.state = Review.State.GENERATED
                review.save(update_fields=['reply', 'state'])

    def add_arguments(self, parser):
        parser.add_argument('--reviewid',
                            action='store',
                            dest='reviewid',
                            default=None,
                            help='reviewid')
