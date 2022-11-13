import requests
import json

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
