from tweepy import API
from django.conf import settings

# Override API class to add new methods that are not offered by tweepy
# e.g account activity functionality
class API(API):
    def request2(self, method, url, params={}):
        # Apply authentication
        auth = None
        if self.auth:
            auth = self.auth.apply_auth()

        resp = self.session.request(method, url, auth=auth, params=params)

        # We get 204s when subscribing
        if resp.status_code not in [200, 204]:
            print(resp.json())

        return resp  # resp.content for media files

    def get_dm_media(self, **kwargs):
        # We only need URL, authentication has been handled
        return self.request('GET', kwargs.get("url"))

    def registerWebHook(self, **kwargs):
        return self.request2(
            "POST",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/webhooks.json",
            {"url": kwargs.get("url")}
        ).json()

    def deleteWebhook(self, **kwargs):
        return self.request2(
            "DELETE",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/webhooks/{kwargs.get('webhook_id')}.json"
        ).content

    def getWebHooks(self):
        return self.request2(
            "GET",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/webhooks.json"
        ).json()

    # subscribe to the currently authenticated user
    # For now we can only support 15 accounts/subscriptions
    def subscribeToUser(self):
        return self.request2(
            "POST",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/subscriptions.json"
        )

    def getSubscriptions(self):
        return self.request2(
            "GET",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/subscriptions/list.json"
        ).json()


    def deleteSubscription(self):
        return self.request2(
            "DELETE",
            f"https://api.twitter.com/1.1/account_activity/all/{settings.DEV_ENV}/subscriptions.json"
        )
