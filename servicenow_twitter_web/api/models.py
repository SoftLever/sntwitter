from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
	# Servicenow credentials
	servicenow_sys_id = models.CharField(max_length=100)
	servicenow_username = models.CharField(max_length=100) # will be equivalent to the customer's twitter ID
	servicenow_password = models.CharField(max_length=100)

	# Custom fields
	custom_fields = models.JSONField(default=dict)

	user = models.ForeignKey(User, on_delete=models.CASCADE) # The user this customer is associated with

	class Meta:
		db_table = "customer"
