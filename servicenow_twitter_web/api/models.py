from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
	# Servicenow credentials
	servicenow_sys_id = models.CharField(max_length=100)
	servicenow_username = models.CharField(max_length=100) # will be equivalent to the customer's twitter ID
	servicenow_password = models.CharField(max_length=100)

	# Custom fields
	# custom_fields = models.JSONField(default=dict)
	first_name = models.CharField(max_length=100, null=True)
	last_name = models.CharField(max_length=100, null=True)
	phone_number = models.CharField(max_length=100, null=True)
	email = models.EmailField(null=True)
	national_id = models.CharField(max_length=100, null=True)

	language = models.CharField(max_length=10, choices=[('ar-sa', 'ar-sa'), ('en', 'en')], default="en") # ISO-639 language codes
	# Language can be changed with every new interaction

	user = models.ForeignKey(User, on_delete=models.CASCADE) # The user this customer is associated with

	class Meta:
		db_table = "customer"
