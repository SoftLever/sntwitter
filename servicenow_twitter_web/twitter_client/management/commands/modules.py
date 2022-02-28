import requests
from django.conf import settings
import tweepy


# Root Auth - The consumer secret and access tokens for the developer
# app we're using
def getAuth(context="user"):
    if context == "user":
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET
        )

        auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    elif context == "application":
        auth = tweepy.AppAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)

    return auth
