# Generated by Django 3.1.7 on 2022-01-18 14:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicenow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_url', models.CharField(max_length=200)),
                ('admin_user', models.CharField(max_length=40)),
                ('admin_password', models.CharField(max_length=40)),
                ('customer_user', models.CharField(max_length=40)),
                ('customer_password', models.CharField(max_length=40)),
                ('customer_account', models.CharField(max_length=40)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
