# Generated by Django 5.1b1 on 2024-09-16 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_alter_buyerprofile_options_remove_buyerprofile_email_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BuyerProfile',
        ),
    ]
