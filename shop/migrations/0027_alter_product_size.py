# Generated by Django 5.1b1 on 2024-09-12 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0026_alter_product_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='size',
            field=models.BooleanField(blank=True, max_length=255, verbose_name='Размеры'),
        ),
    ]
