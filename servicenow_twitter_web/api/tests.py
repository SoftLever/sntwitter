import requests
import json

response = requests.post(
    # "https://twittnow.softlever.com/twitter-activity",
    "http://127.0.0.1:8000/twitter-activity",
    headers={
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "for_user_id": "1469625174244868097",
        "direct_message_events": [
            {
                "type": "message_create",
                "message_create": {
                    "sender_id":"1084028173082419200",
                    "target":{
                        "recepient_id":"1469625174244868097"
                    },
                    "message_data": {
                        "text": "What do you need from me?"
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
