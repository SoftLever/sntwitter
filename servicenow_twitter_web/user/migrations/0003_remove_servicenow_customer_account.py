# Generated by Django 3.1.7 on 2022-01-19 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_servicenow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicenow',
            name='customer_account',
        ),
    ]
