import googleapiclient
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from reviews.services.exceptions import ReplyTooLong, ReviewNotFound


class AndroidPublisherService:

    def __init__(self, info):
        self._credentials = Credentials.from_service_account_info(info)

    def get_service(self):
        return build("androidpublisher", "v3", credentials=self._credentials)

    def reply(self, package_name, review_id, text):
        service = self.get_service()
        reply_request = service.reviews().reply(body={"replyText": text}, packageName=package_name,
                                                reviewId=review_id)
        try:
            response = reply_request.execute()
        except googleapiclient.errors.HttpError as e:
            if e.status_code == 404:
                raise ReviewNotFound('ReviewNotFound')
            if e.reason == 'Reply too long.':
                print(len(text))
                raise ReplyTooLong(e)
            print(e, e.reason)
            return
        return True

    def list_all(self, package_name, num_reviews=100, translationLanguage='en'):
        service = self.get_service()

        reviews = service.reviews().list(
            packageName=package_name,
            maxResults=num_reviews,
            translationLanguage=translationLanguage
        ).execute()

        return reviews

    def get(self, package_name, reviewId, translationLanguage='en'):

        service = self.get_service()

        reviews = service.reviews().get(
            packageName=package_name,
            reviewId=reviewId,
            translationLanguage=translationLanguage
        ).execute()

        return reviews
