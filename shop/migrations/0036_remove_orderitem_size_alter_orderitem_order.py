# Generated by Django 5.1b1 on 2024-09-15 11:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0035_remove_product_size_l_remove_product_size_m_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='size',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.order', verbose_name='Заказ'),
        ),
    ]
