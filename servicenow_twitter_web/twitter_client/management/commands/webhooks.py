from django.core.management.base import BaseCommand
from twitter_client.management.commands.extended_tweepy import API2
import tweepy
from .modules import getAuth
import requests

from django.conf import settings


class Command(BaseCommand):
    help = 'Register new webook'

    # API object with OAuth1
    api = API2(getAuth(), wait_on_rate_limit=True)

    # Application-only auth
    api2 = API2(getAuth("application"), wait_on_rate_limit=True)

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        parser.add_argument('--url', type=str) # if action is register

    def registerWebHook(self, url):
        webhook = self.api.registerWebHook(
            **{"url": url}
        )
        print(webhook)

        return webhook

    def getWebHooks(self):
        webhooks = self.api.getWebHooks()
        print(webhooks)
        return webhooks

    def getSubscriptions(self):
        sub_list = self.api2.getSubscriptions()
        print(sub_list)
        return sub_list

    def handle(self, *args, **options):
        action = options.get("action")

        if action not in ["register", "list", "subscriptions"]:
            print(f"Unrecognized command '{action}'")
            return

        if action == 'register':
            self.registerWebHook(options.get("url"))
        elif action == 'list':
            self.getWebHooks()
        elif action == "subscriptions":
            self.getSubscriptions()

        return


# python manage.py register_webhook https://sntwitter.softlever.com/api/activity
