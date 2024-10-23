import datetime
import random
import re
import time

import django
import googleapiclient
import openai
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from accounts.models import Account
from apps.models import App
from reviews.models import Review
from reviews.services.publisher import AndroidPublisherService

openai.api_key = settings.OPENAI_API_KEY


class Command(BaseCommand):
    help = 'Import reviews'

    _GPC_LANGUAGES = {
        'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy_AM': 'Armenian',
        'az_AZ': 'Azerbaijani', 'bn_BD': 'Bangla', 'eu_ES': 'Basque', 'be': 'Belarusian', 'bg': 'Bulgarian',
        'my_MM': 'Burmese', 'ca': 'Catalan', 'zh_HK': 'Chinese (Hong Kong)', 'zh_CN': 'Chinese (Simplified)',
        'zh_TW': 'Chinese (Traditional)', 'hr': 'Croatian', 'cs_CZ': 'Czech', 'da_DK': 'Danish', 'nl_NL': 'Dutch',
        'en_IN': 'English (India)', 'en_SG': 'English (Singapore)', 'en_ZA': 'English (South Africa)',
        'en_AU': 'English (Australia)', 'en_CA': 'English (Canada)', 'en_GB': 'English (United Kingdom)',
        'et': 'Estonian', 'fil': 'Filipino', 'fi_FI': 'Finnish', 'fr_CA': 'French (Canada)',
        'fr_FR': 'French (France)', 'gl_ES': 'Galician', 'ka_GE': 'Georgian', 'de_DE': 'German', 'el_GR': 'Greek',
        'gu': 'Gujarati', 'iw_IL': 'Hebrew', 'hi_IN': 'Hindi', 'hu_HU': 'Hungarian', 'is_IS': 'Icelandic',
        'id': 'Indonesian', 'it_IT': 'Italian', 'ja_JP': 'Japanese', 'kn_IN': 'Kannada', 'kk': 'Kazakh',
        'km_KH': 'Khmer', 'ko_KR': 'Korean', 'ky_KG': 'Kyrgyz', 'lo_LA': 'Lao', 'lv': 'Latvian', 'lt': 'Lithuanian',
        'mk_MK': 'Macedonian', 'ms': 'Malay', 'ms_MY': 'Malay (Malaysia)', 'ml_IN': 'Malayalam', 'mr_IN': 'Marathi',
        'mn_MN': 'Mongolian', 'ne_NP': 'Nepali', 'no_NO': 'Norwegian', 'fa': 'Persian',
        'fa_AE': 'Persian (United Arab Emirates)', 'fa_AF': 'Persian (Afghanistan)', 'fa_IR': 'Persian (Iran)',
        'pl_PL': 'Polish', 'pt_BR': 'Portuguese (Brazil)', 'pt_PT': 'Portuguese (Portugal)', 'pa': 'Punjabi',
        'ro': 'Romanian', 'rm': 'Romansh', 'ru_RU': 'Russian', 'sr': 'Serbian', 'si_LK': 'Sinhala', 'sk': 'Slovak',
        'sl': 'Slovenian', 'es_419': 'Spanish (Latin America)', 'es_ES': 'Spanish (Spain)',
        'es_US': 'Spanish (United States)', 'sw': 'Swahili', 'sv_SE': 'Swedish', 'ta_IN': 'Tamil', 'te_IN': 'Telugu',
        'th': 'Thai', 'tr_TR': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'zu': 'Zulu'
    }

    def import_reviews(self, app, reviews):
        added = 0
        changed = 0
        for item in reviews:
            # print(f"Reviewer: {item['authorName']}")
            if len(item['comments']) > 2:
                print(f"{len(item['comments'])} comments in {item['reviewId']}")
                continue
            for comment in item['comments']:
                if 'userComment' in comment:
                    userComment = item['comments'][0]['userComment']
                    lastModified = timezone.make_aware(datetime.datetime.fromtimestamp(int(userComment['lastModified']['seconds'])))
                    starRating = userComment['starRating']
                    text = userComment['text']
                    originalText = userComment.get('originalText', '')
                    review, created = Review.objects.get_or_create(uuid=item['reviewId'], defaults=dict(
                        user_id=app.account.user_id,
                        app=app,
                        author=item.get('authorName', ''),
                        text=text,
                        originalText=originalText,
                        lastModified=lastModified,
                        starRating=starRating,
                        thumbsUpCount=userComment.get('thumbsUpCount', 0),
                        thumbsDownCount=userComment.get('thumbsDownCount', 0),
                        reviewerLanguage=userComment['reviewerLanguage'],
                        device=userComment.get('device', ''),
                        androidOsVersion=userComment['androidOsVersion'],
                        appVersionCode=userComment.get('appVersionCode', 0),
                        appVersionName=userComment.get('appVersionName', ''),
                    ))
                    if created:
                        added += 1
                    else:
                        # Lookup changes
                        fields_changed = []
                        if review.thumbsUpCount != userComment.get('thumbsUpCount', 0):
                            review.thumbsUpCount = userComment['thumbsUpCount']
                            fields_changed.append('thumbsUpCount')
                        if review.thumbsDownCount != userComment.get('thumbsDownCount', 0):
                            review.thumbsDownCount = userComment['thumbsDownCount']
                            fields_changed.append('thumbsDownCount')
                        if review.lastModified != lastModified and review.lastModifiedChanged != lastModified:
                            print(f"lastModified {review.lastModified} -> {lastModified} {review.author} {review.id}")
                            review.lastModifiedChanged = lastModified
                            fields_changed.append('lastModifiedChanged')
                        if review.starRating != starRating and review.starRatingChanged != starRating:
                            print(f"starRating {review.starRating} -> {starRating} {review.author} {review.uuid}")
                            review.starRatingChanged = starRating
                            fields_changed.append('starRatingChanged')

                        if review.originalText and review.text != text and review.textChanged != text:
                            print(f"text {review.text} -> {text} {review.author} {review.uuid}")
                            review.textChanged = text
                            fields_changed.append('textChanged')
                        if review.originalText != originalText:
                            review.originalText = originalText
                            fields_changed.append('originalText')

                        if fields_changed:
                            changed += 1
                            review.save(update_fields=fields_changed)
                elif 'developerComment' in comment:
                    try:
                        review = Review.objects.get(uuid=item['reviewId'])
                    except Review.DoesNotExist:
                        print("Review does not exist")
                        review = None
                    if review:
                        lastModified = timezone.make_aware(datetime.datetime.fromtimestamp(
                            int(comment['developerComment']['lastModified']['seconds'])))
                        text = comment['developerComment']['text']
                        if review.reply != text:
                            review.reply = text
                            review.replied = lastModified
                            review.state = Review.State.COMPLETE
                            review.save(update_fields=['reply', 'replied', 'state'])

        return added, changed

    def harvest_reviews(self, app: App):
        used = []
        for lang in self._GPC_LANGUAGES.keys():
            url = f"https://play.google.com/store/apps/details?id={app.packageName}&hl={lang}&gl=US"
            print(url)
            response = requests.get(url)
            for r in re.findall(r'data-review-id="([\w-]+)"', response.text):
                print(r)
                if r in used:
                    continue
                used.append(r)
                yield r
            time.sleep(1)

    def handle(self, **options):
        packageName = options['packageName']
        account_id = options['account']
        if options['reviewid']:
            try:
                review = Review.objects.get(uuid=options['reviewid'])
                if options['packageName'] and options['packageName'] != review.app.packageName:
                    print("Review does not belong to the app")
                    return
                packageName = review.app.packageName
                account_id = review.app.account_id
            except Review.DoesNotExist:
                if not options['packageName']:
                    print(f"Review {options['reviewid']} not found and packageName not specified")
                    return

        qs = Account.objects.filter(state=Account.State.ACTIVE, user__is_active=True)
        if account_id:
           qs = qs.filter(id=account_id)
        for account in qs:
            if options['verbosity'] >= 2:
                print(f"Account: {account}")
            publisher = AndroidPublisherService(account.info)
            qs_apps = account.app_set.filter(state=App.State.ACTIVE)
            if packageName:
                qs_apps = qs_apps.filter(packageName=packageName)
            for app in qs_apps:
                if options['verbosity'] >= 2:
                    print(f"App: {app}")

                if app.harvest:
                    added = 0
                    changed = 0
                    total = 0
                    for review_id in self.harvest_reviews(app):
                        try:
                            review = publisher.get(app.packageName, review_id)
                        except googleapiclient.errors.HttpError as e:
                            print(e)
                            continue
                        try:
                            Review.objects.get(uuid=review['reviewId'])
                        except Review.DoesNotExist:
                            added_review, changed_review = self.import_reviews(app, [review])
                            added += added_review
                            changed += changed_review
                            total += 1
                            time.sleep(1)
                    app.harvest = False
                    app.save(update_fields=['harvest'])
                    print(
                        f"Added {added} of {total} and changed {changed} for {app.packageName}")

                if options['reviewid']:
                    review = publisher.get(app.packageName, options['reviewid'])
                    response = dict(reviews=[review])
                else:
                    response = publisher.list_all(app.packageName, app.num_reviews)

                added, changed = self.import_reviews(app, response['reviews'])
                print(f"Added {added} of {len(response['reviews'])} and changed {changed} for {app.packageName}")

    def add_arguments(self, parser):
        parser.add_argument('--reviewid',
                            action='store',
                            dest='reviewid',
                            default=None,
                            help='reviewid')

        parser.add_argument('--account',
                            action='store',
                            dest='account',
                            type=int,
                            default=None,
                            help='account')

        parser.add_argument('--packageName',
                            action='store',
                            dest='packageName',
                            default=None,
                            help='packageName')
