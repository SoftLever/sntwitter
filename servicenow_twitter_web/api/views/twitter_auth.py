from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.models import Twitter

import re

from django.conf import settings

# Interact with the twitter API
import tweepy
from twitter_client.management.commands.extended_tweepy import API

# Webhook app verification
import base64
import hashlib
import hmac


# We'll use generic views becuase both endpoints need only a GET method

class GetUrl(APIView):
    def get(self, request):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            f"{settings.CALLBACK_URL}?user_id={request.user.id}"
        )

        # Get redirect URL
        try:
            redirect_url = auth.get_authorization_url()
            return Response({"url": redirect_url}, status.HTTP_200_OK)
        except tweepy.TweepyException as e:
            return Response({"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class Subscribe(APIView):
    # This endpoint requires no authentication
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        #print(authentication_classes)
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET
        )

        auth_token = request.GET['oauth_token']
        verifier = request.GET['oauth_verifier']
        user = request.GET['user_id']

        auth.request_token = {'oauth_token': auth_token, 'oauth_token_secret': verifier}

        access_keys = auth.get_access_token(verifier)

        # Get user id and save credentials
        Twitter.objects.filter(user=user).delete()
        auth_instance = Twitter(
            access_token=access_keys[0],
            access_token_secret=access_keys[1]
        )

        auth.set_access_token(auth_instance.access_token, auth_instance.access_token_secret)
        user_details = API(auth, wait_on_rate_limit=True).verify_credentials()                
        auth_instance.userid = str(user_details.id)
        auth_instance.user_id = user
        auth_instance.save()


        # Subscribe to this user's activity
        subscription = API(auth, wait_on_rate_limit=True).subscribeToUser()
        print(subscription)

        return Response({"message": "Subscribed to user"}, status.HTTP_200_OK)


class Unsubscribe(APIView):
    def delete(self, request):
        twitter_instance = Twitter.objects.get(user=request.user)
        auth = tweepy.OAuth1UserHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            twitter_instance.access_token,
            twitter_instance.access_token_secret
        )
        unsub = API(auth, wait_on_rate_limit=True).deleteSubscription()
        return response({"message": "Unsubscribed"}, status.HTTP_204_NO_CONTENT)
