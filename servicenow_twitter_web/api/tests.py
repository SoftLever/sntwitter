import requests
import json

import tweepy
import os

def testTwitterActivity():
    response = requests.post(
        # "https://twittnow.softlever.com/twitter-activity",
        "http://127.0.0.1:8000/twitter-activity",
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "for_user_id": "1084028173082419200",
            "direct_message_events": [
                {
                    "type": "message_create",
                    "message_create": {
                        "sender_id":"2829183065",
                        "target":{
                            "recepient_id":"1084028173082419200"
                        },
                        "message_data": {
                            "text": "English",
                            "quick_reply_response": {
                                "metadata": "ar-sa"
                            }
                        }
                    }
                }
            ]
        })
    )


    if response.status_code == 200:
        print(response.json())
    else:
        print(response)

    return


def testDirectMessage():
    auth = tweepy.OAuthHandler(os.environ.get("API_KEY"), os.environ.get("API_KEY_SECRET"))
    auth.set_access_token(os.environ.get("ACCESS_TOKEN"), os.environ.get("ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth, wait_on_rate_limit=True)

    dm = api.send_direct_message(
        recipient_id='1084028173082419200',
        text="Which service do you need help with?",
        quick_reply_options=[
            {"label": "Registration","metadata":"en"},
            {"label": "Order", "metadata":"ar-sa"}
        ]
    )

    return

testDirectMessage()
