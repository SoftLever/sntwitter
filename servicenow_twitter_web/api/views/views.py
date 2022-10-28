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

from password_generator import PasswordGenerator

from api.models import Customer

from user.models import CustomFields

import re


def validateCutomFields(sys_user, customer_details, message):
    # Retrieve all Twittnow user custom fields
    custom_fields = CustomFields.objects.filter(user=sys_user)

    # Check if customer has entered all required custom fields
    customer_custom_fields = customer_details.custom_fields

    # We need a few things from you before we raise a ticket. Enter the in this order;

    message = "نحتاج منك بعض الأشياء قبل أن نرفع تذكرة. أدخل في هذا الترتيب ؛\n"
    
    for x in custom_fields:
        # if the field is empty send a message and return None
        # None indicates that not all custom fields had been entered
        if not customer_custom_fields.get(x.field_name_stripped):
            message = f"{message}\n{(x.message)}"
            # customer_custom_fields.custom_fields[x.field_name_stripped] = message
            # customer_custom_fields.save()
            # Send the message to Twitter
    return message

    # return None # If this is returned, it means all fields have been filled


def getCustomerDetails(sn, sys_user, customer_username):
    print("Getting customer details")
    # Check if the sender is already the recepient's customer in our database
    try:
        customer_details = Customer.objects.get(user=sys_user, servicenow_username=customer_username)
    except Customer.DoesNotExist:
        print("No customer account found. Creating...")
        customer_details = createNewUser(sn, customer_username, sys_user)

    return customer_details


def getCase(sn, customer_details):
    response = requests.get(
        f"{sn.instance_url}/api/sn_customerservice/case?sys_created_by={customer_details.servicenow_sys_id}^active=1",
        auth=(customer_details.servicenow_username, customer_details.servicenow_password),
    )

    if response.status_code == 401:
        print("Customer user authentication failed. Possible reasons; Customer account deleted on Servicenow, Customer account credentials changed") # Send to logs instead
        return None


    case = response.json().get("result")

    return case


def createCase(sn, customer_details, message, send_as_admin):
    if send_as_admin:
        print("Calling SNOW instance as admin")
        servicenow_credentials = (sn.admin_user, sn.admin_password)
    else:
        print("Calling SNOW instance as customer user")
        servicenow_credentials = (customer_details.servicenow_username, customer_details.servicenow_password)

    case_response = requests.post(
        f"{sn.instance_url}/api/sn_customerservice/case",
        auth=servicenow_credentials,
        data=json.dumps(
            {
                "contact_type": "social",
                "short_description": message,
            }
        )
    )

    case = case_response.json()

    return case


def updateCase(case, sn, customer_details, message, send_as_admin):
    if send_as_admin:
        servicenow_credentials = (sn.admin_user, sn.admin_password)
    else:
        servicenow_credentials = (customer_details.servicenow_username, customer_details.servicenow_password)

    case_response = requests.put(
        f"{sn.instance_url}/api/sn_customerservice/case/{case}",
        auth=servicenow_credentials,
        params={
            "sysparm_input_display_value": "true"
        },
        data=json.dumps(
            {
                "comments": message,
            }
        )
    )

    case = case_response.json().get("result")

    return case


def createNewUser(sn, customer_username, sys_user):
    # Create a user on Servicenow
    sn_customer_user = requests.post(
        f"{sn.instance_url}/api/now/table/sys_user",
        auth=(sn.admin_user, sn.admin_password),
        data=json.dumps(
            {
                "user_name": customer_username,
            }
        )
    )

    if sn_customer_user.status_code == 201:
        try:
            # Get the returned sys_id
            sys_id = sn_customer_user.json().get("result").get("sys_id")

            # Create a password for the user
            pwo = PasswordGenerator()
            customer_password = pwo.generate()

            requests.put(
                f"{sn.instance_url}/api/now/table/sys_user/{sys_id}",
                auth=(sn.admin_user, sn.admin_password),
                params={
                    "sysparm_input_display_value": "true"
                },
                data=json.dumps(
                    {
                        "user_password": customer_password,
                    }
                )
            )

            # Get the required role
            role_object = requests.get(
                f"{sn.instance_url}/api/now/table/sys_user_role",
                params={
                    "sysparm_fields": "sys_id",
                    "name":"csm_ws_integration"
                },
                auth=(sn.admin_user, sn.admin_password)
            )

            role = role_object.json().get("result")[0].get("sys_id")

            # Assign the user the role
            role_response = requests.post(
                f"{sn.instance_url}/api/now/table/sys_user_has_role",
                auth=(sn.admin_user, sn.admin_password),
                data=json.dumps(
                    {
                        "user": sys_id,
                        "role": role,
                    }
                )
            )

            # Keep records in our DB
            customer_details = Customer.objects.create(
                servicenow_sys_id=sys_id,
                servicenow_username=customer_username,
                servicenow_password=customer_password,
                user=sys_user
            )
        except Exception as e:
            print(e) # Send to log file instead
            return None
    else:
        print(f"{sn_customer_user.status_code}: Failed to create user")
        return

    return customer_details


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
        auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
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
            key=bytes(settings.API_KEY_SECRET, 'utf-8'),
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
            keys = Twitter.objects.get(userid=for_user_id)
            userid = keys.userid
            sys_user = keys.user
        except ObjectDoesNotExist:
            return Response({"message": "the user with this twitter account does not exist"})


        # Get Servicenow admin credentials
        try:
            sn = Servicenow.objects.get(user=sys_user)
        except ObjectDoesNotExist:
            return Response({"message": "User has no Servicenow record"})


        sender = None
        target = for_user_id
        message = None
        send_as_admin = False


        # HANDLE DIRECT MESSAGES
        if data.get("direct_message_events"):
            # Get direct message events
            for event in data.get("direct_message_events"):
                if event.get("type") == "message_create":
                    message_create = event.get("message_create")
                    print("Getting Direct message target and sender")
                    sender = message_create.get("sender_id")
                    target = message_create.get("target").get("recipient_id")
                    print(f"{sender} -> {target}")

                    message = message_create.get("message_data").get("text")

                    attachment = message_create.get("message_data", {}).get("attachment", {}).get("media", {}).get("media_url", "")                        

        # HANDLE MENTIONS
        # We know it's a mention if it has the 'user_has_blocked' attribute
        elif data.get("user_has_blocked") is not None:
            for tweet in data.get("tweet_create_events"):
                message = tweet.get("text")
                twitter_username = tweet.get("user").get("screen_name")
                name = tweet.get("user").get("name")
                print("Getting mention sender")
                sender = tweet.get("user").get("id")
                print(sender)

                attachment = None


        # Get customer details
        if not sender:
            return Response({"message": "Request ignored, not a mention or direct message."}, status.HTTP_200_OK)

        if str(sender) == str(userid):
            # We determine whether the message in being received by our user
            # or being sent by from Twitter, by checking sender and userid for equality
            send_as_admin = True
            customer_username = target # If our user is the sender, then we want to create an account for the recepient (their client)
        else:
            customer_username = sender
            send_as_admin = False

        customer_details = getCustomerDetails(sn, sys_user, customer_username)

        if not customer_details:
            return Response({"message": "Failed to retrieve customer details or to create new customer account"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if an open case exists for this customer
        case = getCase(sn, customer_details)
        print(case)

        if case:
            print("Updating case")
            updated_case = updateCase(case[0].get("sys_id"), sn, customer_details, message, send_as_admin)
            print(updated_case)
        else:
            # Validate custom fields -> The function returns none if all fields
            # have been filled. So if it returns none, we will create the case
            # print("Validating custom fields")
            # validate_fields = validateCutomFields(sys_user, customer_details, message)

            # if validate_fields:
            #    return Response({"message": "Received data. Collecting custom fields"}, status.HTTP_200_OK)
            
            print("Creating new case")
            new_case = createCase(sn, customer_details, message, send_as_admin)
            print(new_case)


        return Response({"message": "received data"}, status.HTTP_200_OK)
