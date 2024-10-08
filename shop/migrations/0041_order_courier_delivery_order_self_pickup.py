# Generated by Django 5.1b1 on 2024-09-17 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0040_delete_buyerprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='courier_delivery',
            field=models.BooleanField(default=False, verbose_name='Доставка курьером'),
        ),
        migrations.AddField(
            model_name='order',
            name='self_pickup',
            field=models.BooleanField(default=False, verbose_name='Самовывоз из магазина'),
        ),
    ]
