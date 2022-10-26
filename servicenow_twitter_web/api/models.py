from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
	twitter_id = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE) # The user this customer is associated with

	class Meta:
		db_table = "customer"