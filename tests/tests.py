import requests

update_case = requests.post(
	"https://flowxo.com/hooks/a/ddmk9px8",
	data={"message": "New message goes here", "response_link": "https://twittnow.softlever.com/events?customer_id=67"}
)

print(update_case.status_code)
print(update_case.__dict__)
