from django.core.management.base import BaseCommand
from .extended_tweepy import API
import tweepy

from django.conf import settings


class Command(BaseCommand):
    help = 'Register new webook'

    # API object with OAuth1
    auth = tweepy.OAuth1UserHandler(
        settings.API_KEY, settings.API_KEY_SECRET,
        settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET
    )

    api = API(auth, wait_on_rate_limit=True)

    # Application-only auth
    auth2 = tweepy.OAuth2AppHandler(
        settings.API_KEY, settings.API_KEY_SECRET,
    )

    api2 = API(auth2, wait_on_rate_limit=True)

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        parser.add_argument('--url', type=str) # if action is register
        parser.add_argument('--webhook_id', type=str)

    def registerWebHook(self, url):
        webhook = self.api.registerWebHook(
            **{"url": url}
        )
        print(webhook)

        return webhook

    def deleteWebhook(self, webhook_id):
        response = self.api.deleteWebhook(
            **{"webhook_id": webhook_id}
        )
        print(response)

        return response

    def getWebHooks(self):
        webhooks = self.api.getWebHooks()
        print(webhooks)
        return webhooks

    def getSubscriptions(self):
        sub_list = self.api2.getSubscriptions()
        print(sub_list)
        return sub_list


    def subscribeToUser(self):
        response = self.api.subscribeToUser()
        print(response)
        return response

    def handle(self, *args, **options):
        action = options.get("action")

        if action not in ["register", "list", "subscriptions","delete", "subscribe"]:
            print(f"Unrecognized command '{action}'")
            return

        if action == 'register':
            self.registerWebHook(options.get("url"))
        elif action == 'list':
            self.getWebHooks()
        elif action == "subscriptions":
            self.getSubscriptions()
        elif action == "delete":
            self.deleteWebhook(options.get("webhook_id"))
        elif action == "subscribe":
            self.subscribeToUser()

        return
