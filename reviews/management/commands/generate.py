import openai
from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Review
from reviews.services.generator import ReplyGenerator

openai.api_key = settings.OPENAI_API_KEY


class Command(BaseCommand):
    help = 'Generate replies'

    def handle(self, **options):
        reviewerLanguage = input("Language [en]:") or 'en'
        authorName = input("Author [User Name]:") or 'Mk Savage'
        starRating = input("Stars [5]:") or 5
        text = input("Text:") or "Only rating this a 1 because I'm forced to be one skin color put some other skin colors and sure I'll play this game"
        keyword = input("Keyword:") or 'play survival games'
        reply_generator = ReplyGenerator()
        text = reply_generator.generate_reply(text=text,
                                              lang=reviewerLanguage,
                                              starRating=starRating,
                                              authorName=authorName,
                                              keyword=keyword)
        print(text)
