import requests
from django.conf import settings
import tweepy


SERVICENOW_HEADERS = {"Content-Type":"application/json","Accept":"application/json"}

root_url = settings.SERVICENOW_URL


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


def getExistingCase(twitter_id):
    # Set the request parameters
    url = f'{root_url}/api/sn_customerservice/case'

    # Do the HTTP request
    response = requests.get(
        url,
        auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
        headers=SERVICENOW_HEADERS,
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


def getAccountID():
    url = f'{root_url}/api/now/account'

    response = requests.get(
        url,
        auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PWD),
        headers=SERVICENOW_HEADERS,
        params={"sysparm_query": f"number={settings.SN_TWITTER_CASE_ACCOUNT}"}
    )

    if response.status_code != 200: 
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

    data = response.json()
    sys_id = data.get("result")[0].get("sys_id")

    return sys_id


# create a new case for a client with no case opened
def createCase(description,user_id, username, name, attachment):
    print(f"Creating new case for {user_id}: {description}")

    auth = (settings.SERVICENOW_CUSTOMER_ACCOUNT, settings.SERVICENOW_CUSTOMER_ACCOUNT_PWD)

    response = requests.post(
        f'{root_url}/api/sn_customerservice/case',
        auth=auth,
        headers=SERVICENOW_HEADERS,
        data='{"account": "%s", "short_description": "%s", "u_twitter_user_id": "%s", "u_twitter_username": "%s"}' % (getAccountID(), description, user_id, f"{name} ({username})")
    )

    if response.status_code != 201:
      print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

    data = response.json().get("result")

    return data # case sys id and number


# update an existing case from twitter DM update
def updateCase(case_id, notes, attachment):
    print(f"Updating case {case_id}:\n{notes}")

    auth = (settings.SERVICENOW_CUSTOMER_ACCOUNT, settings.SERVICENOW_CUSTOMER_ACCOUNT_PWD)

    response = requests.put(
        f"{root_url}/api/sn_customerservice/case/{case_id}",
        auth=auth,
        headers=SERVICENOW_HEADERS,
        data='{"comments": "%s"}' % notes
    )

    return
