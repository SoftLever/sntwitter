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

from google.protobuf.json_format import MessageToDict

def sendTwitterDirectMessage(keys, recipient_id, message):
    # AUTHENTICATE TWITTER
    auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    api = API(auth, wait_on_rate_limit=True)

    dm = api.send_direct_message(
        recipient_id=recipient_id,
        text=message
    )

    return dm


def detect_intent_texts(customer_details, text, language_code, keys, customer_twitter_id, sn):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    from google.cloud import dialogflow_v2beta1 as dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(settings.DIALOGFLOW_PROJECT_ID, customer_details.servicenow_username)
    print("Session path: {}\n".format(session))

    # Since we're using a SW agent in place of an arabic one
    if language_code == "ar-sa":
        language_code = "sw"

    # Append tnow to text -> We are using a single intent with only one phrase
    # The only training phrase for this intent is "tnow", so appending it to our
    # texts will trigger it

    print("appending learning phrase to text")
    text = f"{text} tnow001"

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input, } # "query_params": query_params
    )

    response_json = MessageToDict(response._pb)

    print("=" * 20)
    print("Query text: {}".format(response_json.get("queryResult", {}).get("queryText")))
    print(
        "Detected intent: {} (confidence: {})\n".format(
            response_json.get("queryResult").get("intent").get("displayName"),
            response_json.get("queryResult").get("intentDetectionConfidence"),
        )
    )

    fulfillment_text = response_json.get("queryResult").get("fulfillmentText")

    print(f"Fulfillment text: {fulfillment_text}\n")

    sendTwitterDirectMessage(keys, customer_twitter_id, fulfillment_text)

    parameters = response_json.get("queryResult", {}).get("parameters")

    if response.query_result.all_required_params_present and parameters:
        first_name = parameters.get("FirstName", {}).get("name", "John").replace("tnow001", "")
        last_name = parameters.get("LastName", {}).get("name", "Doe").replace("tnow001", "")
        email = parameters.get("Email").replace("tnow001", "")
        phone_number = parameters.get("PhoneNumber").replace("tnow001", "")
        national_id = parameters.get("NationalID").replace("tnow001", "")

        print("Creating case")
        message = f"Customer Details;\n{'*' * 20}\nFirst Name: {first_name}\nLast Name: {last_name}\nEmail: {email}\nPhone: {phone_number}\nNational ID: {national_id}"

        createCase(sn, customer_details, customer_twitter_id, message)

    return response.query_result


def getCustomerDetails(sn, sys_user, customer_twitter_id, customer_twitter_username, customer_twitter_name):
    print("Getting customer details")
    # Check if the sender is already the recepient's customer in our database
    try:
        customer_details = Customer.objects.get(user=sys_user, servicenow_username=customer_twitter_id)
    except Customer.DoesNotExist:
        print("No customer account found. Creating...")
        customer_details = createNewUser(sn, customer_twitter_id, sys_user, customer_twitter_username, customer_twitter_name)

    return customer_details


def getCase(sn, customer_details):
    response = requests.get(
        f"{sn.instance_url}/api/sn_customerservice/case?sysparm_query=sys_created_by={customer_details.servicenow_username}^active=1^contact_type=social",
        auth=(customer_details.servicenow_username, customer_details.servicenow_password),
    )

    if response.status_code == 401:
        print("Customer user authentication failed. Possible reasons; Customer account deleted on Servicenow, Customer account credentials changed") # Send to logs instead
        return None


    case = response.json().get("result")

    return case


def createCase(sn, customer_details, sender, description):
    servicenow_credentials = (customer_details.servicenow_username, customer_details.servicenow_password)

    print(f"Creating case on Servicenow as {servicenow_credentials[0]}")
    case_response = requests.post(
        f"{sn.instance_url}/api/sn_customerservice/case",
        auth=servicenow_credentials,
        data=json.dumps(
            {
                "contact_type": "social",
                "short_description": f"@{customer_details.twitter_username} via Twitter",
                "comments": description
            }
        )
    )

    case = case_response.json()

    return case


def updateCase(case, sn, customer_details, message, send_as_admin, message_sent_from_app, field="comments"):
    if message_sent_from_app:
        print("Message ignored because it's from a third party app")
        return

    if send_as_admin:
        servicenow_credentials = (sn.admin_user, sn.admin_password)
    else:
        servicenow_credentials = (customer_details.servicenow_username, customer_details.servicenow_password)

    print(f"Updating case {case} as {servicenow_credentials[0]}")

    case_response = requests.put(
        f"{sn.instance_url}/api/sn_customerservice/case/{case}",
        auth=servicenow_credentials,
        params={
            "sysparm_input_display_value": "true"
        },
        data=json.dumps(
            {
                field: message,
            }
        )
    )

    case = case_response.json().get("result")

    return case


def createNewUser(sn, customer_username, sys_user, customer_twitter_username, customer_twitter_name):
    first_name = customer_twitter_name
    last_name = None

    print("Splitting first name from last name")
    customer_name = customer_twitter_name.split(" ")

    if len(customer_name) > 1:
        first_name = customer_name[0]
        last_name = customer_name[-1]

    print(f"Calling Servicenow as admin user to create user {customer_username}")

    # Create a user on Servicenow
    sn_customer_user = requests.post(
        f"{sn.instance_url}/api/now/table/sys_user",
        auth=(sn.admin_user, sn.admin_password),
        data=json.dumps(
            {
                "user_name": customer_username,
                "first_name": first_name,
                "last_name": last_name
            }
        )
    )

    if sn_customer_user.status_code == 201:
        print(f"User {customer_username} created successfully")
        try:
            # Get the returned sys_id
            sys_id = sn_customer_user.json().get("result").get("sys_id")

            # Create a password for the user
            pwo = PasswordGenerator()
            customer_password = pwo.generate()

            print(f"Setting password for user {customer_username}")

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

            print(f"Retrieving sys IDs of required roles;")
            # Get the required roles
            role_object = requests.get(
                f"{sn.instance_url}/api/now/table/sys_user_role",
                params={
                    "sysparm_fields": "sys_id",
                    "sysparm_query":"name=task_editor^ORname=csm_ws_integration"
                },
                auth=(sn.admin_user, sn.admin_password)
            )

            roles = [r.get("sys_id") for r in role_object.json().get("result")]

            print(f"Assinging user {customer_username} csm_ws_integration and task_editor roles")

            for role in roles:
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

            print("Creating customer details record")

            # Keep records in our DB
            customer_details = Customer.objects.create(
                servicenow_sys_id=sys_id,
                servicenow_username=customer_username,
                servicenow_password=customer_password,
                user=sys_user,
                twitter_username=customer_twitter_username,
                twitter_name=customer_twitter_name
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
        user = request.user
        message = request.POST.get("message")

        try:
            target = Customer.objects.get(servicenow_sys_id=request.POST.get("target")).servicenow_username
        except Customer.DoesNotExist:
            return Response({"message": f"No associated customer was found"})

        print(f"Received request from {user}\nMessage: {message}\nTarget: {target}")

        # Get the authenticated user's Twitter access tokens
        try:
            keys = Twitter.objects.get(user=user)
        except ObjectDoesNotExist:
            return Response({"message": "No Twitter account. Add a twitter account from you dashboard to send messages"})

        dm = sendTwitterDirectMessage(keys, target, message)

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
        print(f"Received event for user with twitter id {for_user_id}")

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


        print("Initializing sender to None")
        sender = None
        target = for_user_id
        print(f"Initializing target to Twittnow user with twitter ID {target}")
        message = None
        send_as_admin = False
        message_sent_from_app = True if data.get("apps") else False
        quick_reply = None
        customer_twitter_id = None
        customer_twitter_name = None
        customer_twitter_username = None

        # AUTHENTICATE TWITTER
        auth = tweepy.OAuthHandler(settings.API_KEY, settings.API_KEY_SECRET)
        auth.set_access_token(keys.access_token, keys.access_token_secret)
        api = API(auth, wait_on_rate_limit=True)

        users = data.get("users") # Get user data to match with user id

        # HANDLE DIRECT MESSAGES
        if data.get("direct_message_events"):
            print("Identified event as a direct message event")
            # Get direct message events
            for event in data.get("direct_message_events"):
                if event.get("type") == "message_create":
                    message_create = event.get("message_create")
                    quick_reply = message_create.get("message_data").get("quick_reply_response")
                    print(f'Setting sender to {message_create.get("sender_id")}')
                    sender = message_create.get("sender_id")
                    print(f'Setting target to {message_create.get("target").get("recipient_id")}')
                    target = message_create.get("target").get("recipient_id")
                    customer_twitter_name = users.get(sender).get("name")
                    customer_twitter_username = users.get(sender).get("screen_name")

                    message = message_create.get("message_data").get("text")

                    attachment = message_create.get("message_data", {}).get("attachment", {}).get("media", {}).get("media_url", "")                        

        # HANDLE MENTIONS
        # We know it's a mention if it has the 'user_has_blocked' attribute
        elif data.get("user_has_blocked") is not None:
            print("Identified event as a mention event")
            for tweet in data.get("tweet_create_events"):
                message = tweet.get("text")
                customer_twitter_name = tweet.get("user").get("name")
                customer_twitter_username = tweet.get("user").get("screen_name")
                print(f'Setting sender to {tweet.get("user").get("id")}')
                sender = tweet.get("user").get("id")

                attachment = None

        # Get customer details
        if not sender:
            print("Ignoring request because it's not a mention or direct message")
            return Response({"message": "Request ignored, not a mention or direct message."}, status.HTTP_200_OK)

        if str(sender) == str(userid):
            print(f"Sender {sender} is the same as twittnow user with twitter id {userid}. Setting send_as_admin flag to True")
            # We determine whether the message in being received by our user
            # or being sent by from Twitter, by checking sender and userid for equality
            send_as_admin = True
            print(f"Setting target to {target}")
            customer_twitter_id = target # If our user is the sender, then we want to create an account for the recepient (their client)
        else:
            print(f"Setting send_as_admin flag to False because sender {sender} is not the same as twittnow user {str(userid)}")
            customer_twitter_id = sender
            send_as_admin = False

        customer_details = getCustomerDetails(sn, sys_user, customer_twitter_id, customer_twitter_username, customer_twitter_name)

        if not customer_details:
            print("Failed to retrieve customer details or to create new customer account")
            return Response({"message": "Failed to retrieve customer details or to create new customer account"}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if an open case exists for this customer
        print("Checking if active case exists")
        case = getCase(sn, customer_details)


        # Check if the message is a request to change language
        if quick_reply:
            print("Language selection message received")
            customer_details.language = quick_reply.get("metadata")
            customer_details.save()
            print("Calling dialogflow after language selection")

            if case:
                sendTwitterDirectMessage(keys, customer_twitter_id, f"You have an active case {case[0].get('number')}")
            else:
                detect_intent_texts(customer_details, message, customer_details.language, keys, customer_twitter_id, sn)

            return Response({"message": "Changed customer language"}, status.HTTP_200_OK)

        if case:
            print(f"{len(case)} active cases exist. Updating the latest entry")
            case_id = case[0].get("sys_id")
            if case[0].get("description", ""):
                print("Updating case comments with new message")
                updateCase(case_id, sn, customer_details, message, send_as_admin, message_sent_from_app)
            else:
                print("Adding description for case")

                if not send_as_admin:
                    updateCase(case_id, sn, customer_details, message, send_as_admin, message_sent_from_app, "description")

                    print("Sending case creation acknowledgement")
                    if customer_details.language == "ar-sa":
                        text = f"{case[0].get('number')} نشكر لك تواصلك مع مركز خدمات الشركاء ونفيدك بأنه تم تسجيل طلبك رقم"
                    else:
                        text = f"Your Case {case[0].get('number')} has been registered with Partners Care System."

                    sendTwitterDirectMessage(keys, customer_twitter_id, text)

            return Response({"message": "Case updated"}, status.HTTP_200_OK)
        else:
            print("No active case exists")

            # Check if send_as_admin is True -> We don't want to generate responses for
            # messages sent by the admin themselves. 
            if not send_as_admin:
                print("Calling dialogflow")
                detect_intent_texts(customer_details, message, customer_details.language, keys, customer_twitter_id, sn)


        return Response({"message": "received data"}, status.HTTP_200_OK)
