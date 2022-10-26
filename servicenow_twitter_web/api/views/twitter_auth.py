from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.models import Twitter

from django.conf import settings

# Interact with the twitter API
import tweepy
from twitter_client.management.commands.extended_tweepy import API

from django.db import IntegrityError


class GetUrl(APIView):
    def get(self, request):
        auth = tweepy.OAuthHandler(
            settings.API_KEY,
            settings.API_KEY_SECRET,
            callback=f"{settings.CALLBACK_URL}/?user_id={request.user.id}"
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
        auth = tweepy.OAuthHandler(
            settings.API_KEY,
            settings.API_KEY_SECRET
        )

        auth_token = request.GET.get('oauth_token')
        verifier = request.GET.get('oauth_verifier')
        user = request.GET.get('user_id')

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
        auth_instance.handle = user_details.screen_name
        auth_instance.profile_image = user_details.profile_image_url
        try:
            auth_instance.save()
        except IntegrityError:
            return Response({"message": "Subscription already exists for a separate account"}, status.HTTP_200_OK)


        # Subscribe to this user's activity
        subscription = API(auth, wait_on_rate_limit=True).subscribeToUser()

        return Response({"message": "Subscribed to user"}, status.HTTP_200_OK)


class Unsubscribe(APIView):
    def delete(self, request):
        try:
            twitter_instance = Twitter.objects.get(user=request.user)
        except Twitter.DoesNotExist:
            return Response({"message": "No Twitter integration found"}, status.HTTP_404_NOT_FOUND)

        auth = tweepy.OAuth1UserHandler(
            settings.API_KEY,
            settings.API_KEY_SECRET,
            twitter_instance.access_token,
            twitter_instance.access_token_secret
        )
        unsub = API(auth, wait_on_rate_limit=True).deleteSubscription()
        twitter_instance.delete() # Delete Twitter records
        return Response({"message": "Unsubscribed"}, status.HTTP_204_NO_CONTENT)
