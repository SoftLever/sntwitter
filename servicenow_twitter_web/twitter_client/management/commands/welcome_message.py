from django.core.management.base import BaseCommand
from .extended_tweepy import API
import tweepy

from django.conf import settings

from user.models import Twitter


class Command(BaseCommand):
    help = 'Create a welcome message'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        parser.add_argument('--id', type=str)
        parser.add_argument('--name', type=str)
        parser.add_argument('--text', type=str) # if action is register
        parser.add_argument('--quick_reply_options', type=str, nargs="+")
        parser.add_argument('--user_id', type=str, required=True) # The user id to perform the action for

    def createWelcomeMessage(self, api, **options):
        response = api.createWelcomeMessage(
            **{
                  "name": options.get("name"),
                  "text": options.get("text"),
                  "quick_reply_options": options.get("quick_reply_options")
            }
        )
        print(response)
        return response

    def listWelcomeMessages(self, api):
        response = api.listWelcomeMessages()
        print(response)
        return response

    def listWelcomeMessageRules(self, api):
        response = api.listWelcomeMessageRules()
        print(response)
        return response

    def handle(self, *args, **options):
        action = options.get("action")
        user_id = options.get("user_id")

        tokens = Twitter.objects.get(user__id=user_id)

        # API object with OAuth1
        auth = tweepy.OAuth1UserHandler(
            settings.API_KEY, settings.API_KEY_SECRET,
            tokens.access_token, tokens.access_token_secret
        )

        api = API(auth, wait_on_rate_limit=True)

        if action not in ["create", "list", "delete", "create_rule", "list_rules", "delete_rule"]:
            print(f"Unrecognized command '{action}'")
            return

        if action == 'create':
            self.createWelcomeMessage(api, **options)
        elif action == 'list':
            self.listWelcomeMessages(api)
        elif action == 'delete':
            api.deleteWelcomeMessage(options.get("id"))
        elif action == "create_rule":
            api.createWelcomeMessageRule(options.get("id"))
        elif action == "list_rules":
            self.listWelcomeMessageRules(api)
        elif action == "delete_rule":
            api.deleteWelcomeMessageRule(options.get("id"))

        return
