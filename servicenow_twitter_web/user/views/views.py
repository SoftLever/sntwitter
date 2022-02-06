from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate, login, logout

from user.models import Servicenow

from twitter_client.models import Twitter

# For activity deactivation
import tweepy
from twitter_client.management.commands.extended_tweepy import API2

import traceback


def landing(request):
	return render(request, "index.html")


def signup(request):
    # POST adds some complications - We'll use GET
    # for now and switch to POST when implemeting API
    if request.method == "GET" and request.GET.get("first_name"):
        first_name = request.GET.get('first_name')
        last_name = request.GET.get('last_name')
        email = request.GET.get('email')
        company_name = request.GET.get('company_name')
        password = request.GET.get('password')

        User = get_user_model()

        user_instance = User.objects.create_user(
        	username=email, first_name=first_name,
        	last_name=last_name, company_name=company_name,
        	password=password
        )
        user_instance.save()

        # Log in instantly
        user = authenticate(username=email, password=password)
        login(request, user)

    return render(request, "signup.html")


def registerServicenow(request):
    sn_url = request.GET.get('sn_url')
    sn_admin = request.GET.get('sn_admin')
    sn_admin_pwd = request.GET.get('sn_admin_pwd')
    sn_customer = request.GET.get('sn_customer')
    sn_customer_pwd = request.GET.get('sn_customer_pwd')

    sn_instance = Servicenow(
        instance_url=sn_url,
        admin_user=sn_admin,
        admin_password=sn_admin_pwd,
        customer_user=sn_customer,
        customer_password=sn_customer_pwd,
        user=request.user
    )

    sn_instance.save()

    return HttpResponse("Added Servicenow details")


def loginUser(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.method == "POST":
        tid = request.POST.get("twitter_user_id")
        instance = Twitter.objects.filter(twitter_user_id=tid)

        auth = tweepy.OAuthHandler(
            consumer_key=settings.CONSUMER_KEY,
            consumer_secret=settings.CONSUMER_SECRET
        )
        auth.set_access_token(instance[0].twitter_access, instance[0].twitter_access_secret)

        # Unsubscribe from user's activity 
        try:
            unsubscription = API2(auth, wait_on_rate_limit=True).deleteSubscription()
            print(unsubscription)
        except Exception as e:
            print(traceback.format_exc())

        # Delete records from DB
        instance.delete()
        return redirect('dashboard')

    sn_configs = Servicenow.objects.filter(user=request.user)
    twitter = Twitter.objects.filter(user=request.user)
    context = {"servicenow": sn_configs, "twitter": twitter}
    return render(request, 'dashboard/index.html', context)
