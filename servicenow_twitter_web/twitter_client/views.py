from django.http import HttpResponse
from django.shortcuts import redirect

from django.conf import settings

from django.contrib.auth.decorators import login_required

import tweepy

from .models import Twitter

# For activity subscription
from twitter_client.management.commands.extended_tweepy import API2

import traceback


def getAuth():
    auth = tweepy.OAuthHandler(
        settings.CONSUMER_KEY,
        settings.CONSUMER_SECRET,
        settings.CALLBACK_URL
    )

    return auth

def get_redirect_url():

    auth = getAuth()

    try:
        redirect_url = auth.get_authorization_url()
        return redirect_url
    except tweepy.TweepyException as e:
        print(e)
        return 'error'


def finish_authorization(token, verifier):
    auth = getAuth()

    auth.request_token = {'oauth_token': token, 'oauth_token_secret': verifier}

    try:
        access_rights = auth.get_access_token(verifier)
        print(access_rights)
        return access_rights

    except tweepy.TweepyException:
        return HttpResponse('Error! Failed to get access token.')

@login_required
def redirect_user(request):
    redirect_url = get_redirect_url()

    if redirect_url == 'error':
        return HttpResponse('Something went wrong')
    else:
        return redirect(redirect_url)

@login_required
def save_access_tokens(request):
    auth_token = request.GET['oauth_token']
    verifier = request.GET['oauth_verifier']

    access_keys = finish_authorization(auth_token, verifier)

    twitter_instance = Twitter(
        twitter_access=access_keys[0],
        twitter_access_secret=access_keys[1]
    )

    auth = tweepy.OAuthHandler(
        consumer_key=settings.CONSUMER_KEY,
        consumer_secret=settings.CONSUMER_SECRET
    )
    auth.set_access_token(twitter_instance.twitter_access, twitter_instance.twitter_access_secret)

    # Get user details
    user_details = tweepy.API(auth, wait_on_rate_limit=True).verify_credentials()
    name = user_details.name

    twitter_instance.twitter_username = user_details.screen_name
    twitter_instance.twitter_user_id = user_details.id_str
    twitter_instance.profile_image = user_details.profile_image_url

    # Subscribe to this user's activity 
    try:
        subscription = API2(auth, wait_on_rate_limit=True).subscribeToUser()
        print(subscription)
    except Exception as e:
        print(traceback.format_exc())

    # Associate this twitter account with currently logged in user
    twitter_instance.user = request.user

    twitter_instance.save()

    return redirect('dashboard')
