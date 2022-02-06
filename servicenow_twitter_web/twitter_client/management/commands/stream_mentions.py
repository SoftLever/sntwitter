import tweepy
from django.conf import settings
from django.core.management.base import BaseCommand

from twitter_client.models import Keys, ReceivedMessages
from .modules import updateCase, createCase, getExistingCase


class TweetStreamer(tweepy.Stream):
    def on_status(self, status):
        try:
            tweet_id = status.id
            text = status.text
            username = status.user.screen_name
            name = status.user.name
            user_id = status.user.id
            attachment = None

            cases = getExistingCase(user_id)

            if cases:
                case_id = cases[0].get("sys_id")
                updateCase(case_id, text, attachment)
                ReceivedMessages(message_id=tweet_id,sender=user_id,target=settings.TWITTER_USER_ID).save()

            else:
                createCase(text,user_id, username, name, attachment)
                ReceivedMessages(message_id=tweet_id,sender=user_id,target=settings.TWITTER_USER_ID).save()

        except Exception as e:
            print(e)



class Command(BaseCommand):
    help = 'Stream tweets based on mentions'

    def handle(self, *args, **options):
        # Get API keys from database
        keys = Keys.objects.all().order_by("-id")[0]

        stream = TweetStreamer(
          keys.twitter_consumer, keys.twitter_consumer_secret,
          keys.twitter_access, keys.twitter_access_secret
        )

        stream.filter(track=[settings.TWITTER_USERNAME])
