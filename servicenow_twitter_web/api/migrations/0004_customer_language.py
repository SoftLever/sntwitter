# Generated by Django 4.1.2 on 2022-11-10 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_customer_custom_fields_customer_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='language',
            field=models.CharField(choices=[('ar-sa', 'ar-sa'), ('en', 'en')], default='en', max_length=10),
        ),
    ]