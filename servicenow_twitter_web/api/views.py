from rest_framework.views import APIView

# for API responses
from rest_framework.response import Response
from rest_framework import status

import tweepy

import requests

from django.conf import settings

from twitter_client.models import Twitter
from user.models import Servicenow
from django.contrib.auth import get_user_model

# Webhook app verification
import base64
import hashlib
import hmac

# For processing attachments
from twitter_client.management.commands.modules import getAuth
from twitter_client.management.commands.extended_tweepy import API2
import time

# For checking if event requests are valid
from django.core.exceptions import ObjectDoesNotExist

import traceback


class ServiceNow():
    SERVICENOW_HEADERS = {"Content-Type":"application/json","Accept":"application/json"}

    root_url = settings.SERVICENOW_URL

    api = API2(getAuth(), wait_on_rate_limit=True)


    def snAuth(self, sys_user, is_admin_message):
        # Get user's servicenow records, we'll use the latest instance
        sn_instance = Servicenow.objects.filter(user=sys_user)[0]

        if is_admin_message:
            auth = (sn_instance.instance_url, sn_instance.admin_user, sn_instance.admin_password)
        else:
            auth = (sn_instance.instance_url, sn_instance.customer_user, sn_instance.customer_password)

        return auth  # returns (url, user, password)


    def getExistingCase(self,twitter_id, sys_user, is_admin_message=True):
        auth = self.snAuth(sys_user, is_admin_message)

        # Set the request parameters
        url = f'{auth[0]}/api/sn_customerservice/case'

        # Do the HTTP request
        response = requests.get(
            url,
            auth=(auth[1], auth[2]),
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


    def fileHandle(self, file_url, auth, sys_id):
        # The file URL will be separated by / and the last part will be the file name
        filename = file_url.split("/")[-1]
        file = self.api.get_dm_media(url=file_url)
        requests.post(
            f"{auth[0]}/api/now/attachment/file?file_name={filename}&table_sys_id={sys_id}&table_name=sn_customerservice_case",
            auth=(auth[1], auth[2]),
            headers={"Content-Type": "*/*"},
            data=file
        )
        return


    # create a new case for a client with no case opened
    def createCase(self,description,user_id, username, attachment, sys_user, is_admin_message=False):
        print(f"Creating new case for {user_id}: {description}")

        auth = self.snAuth(sys_user, is_admin_message)

        response = requests.post(
            f'{auth[0]}/api/sn_customerservice/case',
            auth=(auth[1], auth[2]),
            headers=self.SERVICENOW_HEADERS,
            data='{"short_description": "%s", "u_twitter_user_id": "%s", "u_twitter_username": "%s"}' % (description, user_id, username)
        )

        if response.status_code != 201:
          print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

        data = response.json().get("result")

        # Add attachment if there's one
        if attachment:
            self.fileHandle(attachment, auth, data.get("sys_id"))

        return data # case sys id and number


    # update an existing case from twitter DM update
    def updateCase(self,case_id, notes, attachment, sys_user, is_admin_message=False):
        print(f"Updating case {case_id}:\n{notes}")

        auth = self.snAuth(sys_user, is_admin_message)

        response = requests.put(
            f"{auth[0]}/api/sn_customerservice/case/{case_id}",
            auth=(auth[1], auth[2]),
            headers=self.SERVICENOW_HEADERS,
            data='{"comments": "%s"}' % notes
        )

        # Add attachment if there's one
        if attachment:
            self.fileHandle(attachment, auth, case_id)

        return


class Events(APIView):
    SERVICENOW_HEADERS = {"Content-Type":"application/json","Accept":"application/json"}

    def post(self, request):
        user_id = request.POST.get("user_id")
        print(user_id)

        # Check if user exists
        User = get_user_model()
        try:
            sys_user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"Error": "Bad Auth data"}, status.HTTP_401_UNAUTHORIZED)

        message = request.POST.get("message")
        attachment = request.POST.get("attachment")
        target = request.POST.get("target")
        print(message)
        print(target)

        # Get API keys from database
        keys = Twitter.objects.filter(user=sys_user)

        if not keys:
            return Response({"Error": "No Twitter account"})

        # AUTHENTICATE TWITTER
        auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        auth.set_access_token(keys[0].twitter_access, keys[0].twitter_access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        if attachment:
            try:
                # We need Servicenow details to download attachments
                sn = ServiceNow()
                auth = sn.snAuth(sys_user, True)
                # Get attachment details
                attachment_details = requests.get(
                    f"{auth[0]}/api/now/attachment/{attachment}",
                    auth=(auth[1], auth[2]),
                    headers=self.SERVICENOW_HEADERS
                ).json().get("result")

                # Download the attachment
                attachment_url = attachment_details.get("download_link")
                filename = attachment_details.get("file_name")
                file = requests.get(
                    attachment_url,
                    auth=(auth[1], auth[2])
                ).content

                # upload attachment to Twitter
                upload = api.simple_upload(filename=filename, file=file)
                media_id = upload.media_id
            except Exception as e:
                print(f"Failed to upload attachment: {e}")

        # Send message to Twitter
        dm = api.send_direct_message(
            recipient_id=target,
            text=message
        )

        return Response(
            {"tweet_id": dm.id},
            status.HTTP_200_OK
        )


class TwitterActivity(APIView):
    def get(self, request):
        # creates HMAC SHA-256 hash from incomming token and your consumer secret
        sha256_hash_digest = hmac.new(
            key=bytes(settings.CONSUMER_SECRET, 'utf-8'),
            msg=bytes(request.GET.get('crc_token'), 'utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        # construct response data with base64 encoded hash
        response = {
            'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode('ascii')
        }

        return Response(response, status.HTTP_200_OK)


    def post(self, request):
        data = request.data

        # Find the user details associated with activity
        for_user_id = data.get("for_user_id")

        try:
            user_twitter_data = Twitter.objects.filter(twitter_user_id=for_user_id)
            twitter_id = user_twitter_data[0].twitter_user_id
            sys_user = user_twitter_data[0].user
        except Exception:
            # An exception will most likely be a result of not finding records
            print(traceback.format_exc())
            # Twitter did its part, but our app failed for some reason,
            # so we'll still return a 200 to twitter
            return Response({"message": "received data"}, status.HTTP_200_OK)


        # HANDLE DIRECT MESSAGES
        if data.get("direct_message_events"):
            # Get direct message events
            for event in data.get("direct_message_events"):
                if event.get("type") == "message_create":
                    message_create = event.get("message_create")
                    sender = message_create.get("sender_id")
                    target = message_create.get("target").get("recipient_id")
                    # Target should be equal twitter_id. This is how we know this is a received message

                    text = message_create.get("message_data").get("text")

                    try:
                        attachment = message_create.get("message_data").get("attachment").get("media").get("media_url")
                    except Exception as e:
                        attachment = None

                    if target == twitter_id:
                        client_twitter_id = sender
                        is_admin_message = False
                    else:
                        client_twitter_id = target
                        is_admin_message = True

                    # We'll make a servicenow object to create or update case
                    sn = ServiceNow()

                    cases = sn.getExistingCase(client_twitter_id, sys_user)

                    if cases:
                        case_id = cases[0].get("sys_id")
                        sn.updateCase(case_id, text, attachment, sys_user, is_admin_message)

                    else:
                        user = data.get("users").get(client_twitter_id)
                        username = f"{user.get('name')} ({user.get('screen_name')})"
                        sn.createCase(text,client_twitter_id, username, attachment, sys_user, is_admin_message)

        # HANDLE MENTIONS
        # We know it's a mention if it has the 'user_has_blocked' attribute
        elif data.get("user_has_blocked") is not None:
            for tweet in data.get("tweet_create_events"):
                text = tweet.get("text")
                username = tweet.get("user").get("screen_name")
                name = tweet.get("user").get("name")
                user_id = tweet.get("user").get("id")

                attachment = None

                # We'll make a servicenow object to create or update case
                sn = ServiceNow()

                cases = sn.getExistingCase(user_id, sys_user)

                if cases:
                    case_id = cases[0].get("sys_id")
                    sn.updateCase(case_id, text, attachment, sys_user)

                else:
                    sn.createCase(text,user_id, f"{name} ({username})", attachment, sys_user)

        return Response({"message": "received data"}, status.HTTP_200_OK)
