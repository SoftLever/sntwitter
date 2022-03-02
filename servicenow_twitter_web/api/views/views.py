from rest_framework.views import APIView

# for API responses
from rest_framework.response import Response
from rest_framework import status

import requests

from django.conf import settings

from user.models import Twitter
from user.models import Servicenow
from django.contrib.auth import get_user_model

# Webhook app verification
import base64
import hashlib
import hmac

from twitter_client.management.commands.extended_tweepy import API

# For checking if event requests are valid
from django.core.exceptions import ObjectDoesNotExist

import json

import tweepy


class Events(APIView):
    def post(self, request):
        message = request.POST.get("message")
        target = request.POST.get("target")

        # Get the authenticated user's Twitter access tokens
        try:
            keys = Twitter.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"message": "No Twitter account. Add a twitter account from you dashboard to send messages"})

        # AUTHENTICATE TWITTER
        auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        auth.set_access_token(keys.access_token, keys.access_token_secret)
        api = API(auth, wait_on_rate_limit=True)

        # Send message to Twitter
        dm = api.send_direct_message(
            recipient_id=target,
            text=message
        )

        return Response(
            {"message_id": dm.id},
            status.HTTP_200_OK
        )


class TwitterActivity(APIView):
    authentication_classes = []
    permission_classes = []

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
            keys = Twitter.objects.get(userid=for_user_id).prefetch_related("user")
            userid = keys.userid
            sys_user = keys.user
        except ObjectDoesNotExist:
            return Response({"message": "the user with this twitter account does not exist"})


        # Get Servicenow credentials
        try:
            sn = Servicenow.objects.get(user=sys_user)
        except ObjectDoesNotExist:
            return Response({"message": "User has no Servicenow record"})


        # HANDLE DIRECT MESSAGES
        if data.get("direct_message_events"):
            # Get direct message events
            for event in data.get("direct_message_events"):
                if event.get("type") == "message_create":
                    message_create = event.get("message_create")
                    sender = message_create.get("sender_id")
                    target = message_create.get("target").get("recipient_id")
                    # Target should be equal twitter_id. This is how we know this is a received message

                    message = message_create.get("message_data").get("text")

                    attachment = message_create.get("message_data", {}).get("attachment", {}).get("media", {}).get("media_url", "")

                    # if target == userid:
                    #     {"is_admin":"0"}
                    # else:
                    #     {"is_admin":"0"}

                    twitter_username = f"{user.get('name')} ({user.get('screen_name')})"

                    response = requests.post(
                        f"{sn.instance_url}/api/x_745589_sntwitter/create_or_update_case",
                        auth=(sn.admin_user, sn.admin_password),
                        data=json.dumps(
                            {
                                "message": message,
                                "twitter_user_id": twitter_user_id,
                                "twitter_username": twitter_username
                            }
                        )
                    )

        # HANDLE MENTIONS
        # We know it's a mention if it has the 'user_has_blocked' attribute
        elif data.get("user_has_blocked") is not None:
            for tweet in data.get("tweet_create_events"):
                message = tweet.get("text")
                twitter_username = tweet.get("user").get("screen_name")
                name = tweet.get("user").get("name")
                sender = tweet.get("user").get("id")

                attachment = None

                response = requests.post(
                    f"{sn.instance_url}/api/x_745589_sntwitter/create_or_update_case",
                    auth=(sn.admin_user, sn.admin_password),
                    data=json.dumps(
                        {
                            "message": message,
                            "twitter_user_id": sender,
                            "twitter_username": twitter_username
                        }
                    )
                )


        return Response({"message": "received data"}, status.HTTP_200_OK)
