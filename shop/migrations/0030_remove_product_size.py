# Generated by Django 5.1b1 on 2024-09-12 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0029_alter_product_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
    ]
