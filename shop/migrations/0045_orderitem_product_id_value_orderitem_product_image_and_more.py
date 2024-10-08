# Generated by Django 5.1b1 on 2024-09-19 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0044_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_id_value',
            field=models.IntegerField(blank=True, default=1, editable=False, verbose_name='ID товара'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_image',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='products/', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_title',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Название товара'),
        ),
    ]
