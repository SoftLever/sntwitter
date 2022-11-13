from django.core.management.base import BaseCommand
from .extended_tweepy import API
import tweepy

from django.conf import settings


class Command(BaseCommand):
    help = 'Create a welcome message'

    # API object with OAuth1
    auth = tweepy.OAuth1UserHandler(
        settings.API_KEY, settings.API_KEY_SECRET,
        settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET
    )

    api = API(auth, wait_on_rate_limit=True)

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        parser.add_argument('--id', type=str)
        parser.add_argument('--name', type=str)
        parser.add_argument('--text', type=str) # if action is register
        parser.add_argument('--quick_reply_options', type=str, nargs="+")

    def createWelcomeMessage(self, **options):
        response = self.api.registerWelcomeMessage(
            **{
                  "name": options.get("name"),
                  "text": options.get("text"),
                  "quick_reply_options": options.get("quick_reply_options")
            }
        )
        print(response)
        return response

    def listWelcomeMessages(self):
        response = self.api.listWelcomeMessages()
        print(response)
        return response

    def listWelcomeMessageRules(self):
        response = self.api.listWelcomeMessageRules()
        print(response)
        return response

    def handle(self, *args, **options):
        action = options.get("action")

        if action not in ["create", "list", "delete", "create_rule", "list_rules", "delete_rule"]:
            print(f"Unrecognized command '{action}'")
            return

        if action == 'create':
            self.api.createWelcomeMessage(**options)
        elif action == 'list':
            self.listWelcomeMessages()
        elif action == 'delete':
            self.api.deleteWelcomeMessage(options.get("id"))
        elif action == "create_rule":
            self.api.createWelcomeMessageRule(options.get("id"))
        elif action == "list_rules":
            self.listWelcomeMessageRules()
        elif action == "delete_rule":
            self.api.deleteWelcomeMessageRule(options.get("id"))

        return
