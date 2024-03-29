from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class Twitter(models.Model):
    # Primary twitter user info
    twitter_username = models.CharField(max_length=40)
    twitter_user_id = models.CharField(max_length=40)
    profile_image = models.CharField(max_length=200, null=True)
    twitter_access = models.CharField(max_length=200, unique=True)
    twitter_access_secret = models.CharField(max_length=200, unique=True)
    subscription_id = models.CharField(max_length=40, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.twitter_username

    class Meta:
        db_table = "twitter"
