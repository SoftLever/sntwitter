# Generated by Django 4.1.2 on 2022-10-26 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_customfields_id_alter_servicenow_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfields',
            name='field_name_stripped',
            field=models.CharField(default='first_name', max_length=100),
            preserve_default=False,
        ),
    ]