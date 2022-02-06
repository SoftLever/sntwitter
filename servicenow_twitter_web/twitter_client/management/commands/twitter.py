import requests

import time

from django.conf import settings
from django.core.management.base import BaseCommand


import os # for environment variables

import tweepy # to make requests to twitter

from twitter_client.models import Keys, ReceivedMessages

from .extended_tweepy import API2


class Command(BaseCommand):
    help = 'Get Twitter DMs and open or update cases'

    # def add_arguments(self, parser):
    #     parser.add_argument('--triggered_by', type=str, default='cron')

    # Get API keys from database
    keys = Keys.objects.all().order_by("-id")[0]

    # For now we'll work with the most recent set of API keys. This makes an assumption
    # that this is not a SAAS app, so all keys stored in this table belong to the org
    # running the app

    # AUTHENTICATE TWITTER
    auth = tweepy.OAuthHandler(keys.twitter_consumer, keys.twitter_consumer_secret)
    auth.set_access_token(keys.twitter_access, keys.twitter_access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    api_2 = API2(auth, wait_on_rate_limit=True)


    SERVICENOW_HEADERS = {"Content-Type":"application/json","Accept":"application/json"}

    root_url = settings.SERVICENOW_URL


    def getExistingCase(self,twitter_id):
        # Set the request parameters
        url = f'{self.root_url}/api/sn_customerservice/case'

        # Do the HTTP request
        response = requests.get(
            url,
            auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
            headers=self.SERVICENOW_HEADERS,
            params={
                "sysparm_fields": "number,sys_id,sys_updated_on,u_twitter_user_id,u_received_messages",
                "sysparm_query": f"active=true^u_twitter_user_id={twitter_id}"
            }
        )


        # Check for HTTP codes other than 200
        if response.status_code != 200: 
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

        case = response.json().get("result")

        return case


    def getAccountID(self):
        url = f'{self.root_url}/api/now/account'

        response = requests.get(
            url,
            auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
            headers=self.SERVICENOW_HEADERS,
            params={"sysparm_query": f"number={settings.SN_TWITTER_CASE_ACCOUNT}"}
        )

        if response.status_code != 200: 
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

        data = response.json()
        sys_id = data.get("result")[0].get("sys_id")

        return sys_id


    # create a new case for a client with no case opened
    def createCase(self,description,user_id, attachment, is_admin_message=False):
        print(f"Creating new case for {user_id}: {description}")

        if is_admin_message:
            auth = (settings.SERVICENOW_USER, settings.SERVICENOW_PWD)
        else:
            auth = (settings.SERVICENOW_CUSTOMER_ACCOUNT, settings.SERVICENOW_CUSTOMER_ACCOUNT_PWD)

        # Get Twitter username
        user = self.api.get_user(user_id=user_id)
        username = f"{user.name} ({user.screen_name})"

        response = requests.post(
            f'{self.root_url}/api/sn_customerservice/case',
            auth=auth,
            headers=self.SERVICENOW_HEADERS,
            data='{"account": "%s", "short_description": "%s", "u_twitter_user_id": "%s", "u_twitter_username": "%s"}' % (self.getAccountID(), description, user_id, username)
        )

        if response.status_code != 201:
          print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

        data = response.json().get("result")

        # Add attachment if there's one
        if attachment:
            # Get the media
            file = self.api_2.get_dm_media(url=attachment)
            requests.post(
                f"{self.root_url}/api/now/attachment/file?file_name=attachment_{round(time.time())}&table_sys_id={data.get('sys_id')}&table_name=sn_customerservice_case",
                auth=auth,
                headers={"Content-Type": "*/*"},
                data=file
            )

        return data # case sys id and number


    # update an existing case from twitter DM update
    def updateCase(self,case_id, notes, attachment, is_admin_message=False):
        print(f"Updating case {case_id}:\n{notes}")

        if is_admin_message:
            auth = (settings.SERVICENOW_USER, settings.SERVICENOW_PWD)
        else:
            auth = (settings.SERVICENOW_CUSTOMER_ACCOUNT, settings.SERVICENOW_CUSTOMER_ACCOUNT_PWD)

        response = requests.put(
            f"{self.root_url}/api/sn_customerservice/case/{case_id}",
            auth=auth,
            headers=self.SERVICENOW_HEADERS,
            data='{"comments": "%s"}' % notes
        )

        # Add attachment if there's one
        if attachment:
            # Get the media
            file = self.api_2.get_dm_media(url=attachment)
            requests.post(
                f"{self.root_url}/api/now/attachment/file?file_name=attachment_{round(time.time())}&table_sys_id={case_id}&table_name=sn_customerservice_case",
                auth=auth,
                headers={"Content-Type": "*/*"},
                data=file
            )

        return


    # The rate limit for this endpoint is 15 requests every 15 minutes per user
    # so we can run the script every minute, but that's overkill. We'll run every
    # 3 minutes instead
    def getTwitterDirectMessages(self):
        # We need to keep track of messages that have already been sent to
        # servicnow to avoid re-sending
        received_messages = list(ReceivedMessages.objects.all().values_list("message_id", flat=True))


        # messages are returned in reverse chronological order. We want to reverse this
        # because the earliest message marks the point at which a case was opened.
        # We'll have to store all messages in memory first
        messages = []

        for message in tweepy.Cursor(self.api.get_direct_messages, count=50).items():
            messages.append(message)

        for message in reversed(messages):
            message_id = message.id

            if str(message_id) not in received_messages:
                timestamp = int(message.created_timestamp)
                # Current time - timestamp must be <= 3 minutes.
                message_create = message.message_create
                sender = message_create.get("sender_id")
                target = message_create.get("target").get("recipient_id")
                # Target should be equal authenticated user ID. This is how we know this is a received message
                text = message_create.get("message_data").get("text")

                try:
                    attachment = message_create.get("message_data").get("attachment").get("media").get("media_url")
                except Exception as e:
                    attachment = None

                if target == settings.TWITTER_USER_ID:
                    client_twitter_id = sender
                    is_admin_message = False
                else:
                    client_twitter_id = target
                    is_admin_message = True

                cases = self.getExistingCase(client_twitter_id)

                if cases:
                    case_id = cases[0].get("sys_id")
                    self.updateCase(case_id, text, attachment, is_admin_message)
                    ReceivedMessages(message_id=message_id,sender=sender,target=target).save()

                else:
                    self.createCase(text,client_twitter_id, attachment, is_admin_message)
                    ReceivedMessages(message_id=message_id,sender=sender,target=target).save()


        return

    def handle(self, *args, **options):
        self.getTwitterDirectMessages()


# sudo crontab -e

# */5 * * * * python manage.py twitter
