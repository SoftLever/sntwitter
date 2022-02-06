import tweepy
import requests
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings

from twitter_client.models import Keys, ServicenowEvents, ReceivedMessages

import os


class Command(BaseCommand):
    help = 'Send ServiceNow updates to Twitter DMs'

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

    SERVICENOW_HEADERS = {"Content-Type":"application/json","Accept":"application/json"}

    root_url = settings.SERVICENOW_URL

    def getCaseActivities(self):
        url = f'{self.root_url}/api/sn_customerservice/case'

        response = requests.get(
            url,
            auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
            headers=self.SERVICENOW_HEADERS,
            params={"sysparm_fields": "number,sys_id,sys_updated_on,u_twitter_user_id"}
            # "sysparm_query": "active=true" - Filtering by open activities only inhibits
            # sending of the last activity before a case is closed
        )

        # Check for HTTP codes other than 200
        if response.status_code != 200: 
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
            exit()

        cases = response.json().get("result")

        for case in cases:
            twitter_id = case.get("u_twitter_user_id")

            # Only work on cases that have the twitter id field
            if not twitter_id:
                continue

            sys_id = case.get("sys_id")

            # Get activities for this case
            response = requests.get(
                f"{self.root_url}/api/sn_customerservice/case/{sys_id}/activities",
                auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
                headers=self.SERVICENOW_HEADERS,
                params={
                    "sysparm_ activity_type": "attachments,comments"
                    # work notes shouldn't be sent to customer
                }
            )

            activities = response.json().get("result")

            sent_activities = list(ServicenowEvents.objects.all().values_list("event_id", flat=True))

            for activity in activities.get("entries"):
                message = activity.get("value")
                attachment = activity.get("attachment")

                media_id = None

                if attachment:
                    try:
                        # Get attachment details
                        attachment_details = requests.get(
                            f"{self.root_url}/api/now/attachment/{attachment.get('sys_id')}",
                            auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
                            headers=self.SERVICENOW_HEADERS
                        ).json().get("result")

                        # Download the attachment
                        attachment_url = attachment_details.get("download_link")
                        filename = attachment_details.get("file_name")
                        file = requests.get(
                            attachment_url,
                            auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD)
                        ).content

                        # upload attachment to Twitter
                        upload = self.api.simple_upload(filename=filename, file=file)
                        media_id = upload.media_id
                    except Exception as e:
                        print(f"Failed to upload attachment: {e}")

                activity_id = activity.get("sys_id")

                # Send DM to twitter only if activity has been created by a user other than
                # the customer and the activity has not been marked as sent yet
                if activity.get("user_sys_id") != settings.SERVICENOW_CUSTOMER_SYS_ID and activity_id not in sent_activities:
                    if message:
                        print(f"Sending Twitter DM to {twitter_id}:\n{message}")
                        dm = self.api.send_direct_message(
                            recipient_id=twitter_id,
                            text=message
                        )
                    elif attachment:
                        print(f"Sending attachment to {twitter_id}:\n{media_id}")
                        dm = self.api.send_direct_message(
                            text=None,
                            recipient_id=twitter_id,
                            attachment_type="media",
                            attachment_media_id=media_id
                        )
                    else:
                        continue

                    ServicenowEvents(event_id=activity_id).save()
                    # To avoid receiving the same message we sent, we'll save this message as received
                    ReceivedMessages(
                        message_id=dm.id,
                        sender=dm.message_create.get("sender_id"),
                        target=dm.message_create.get("target").get("recipient_id")
                    ).save()

        return

    def handle(self, *args, **options):
        self.getCaseActivities()

# sudo crontab -e

# */5 * * * * python manage.py servicenow
