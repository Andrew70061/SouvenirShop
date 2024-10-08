# Generated by Django 5.1b1 on 2024-09-12 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0022_product_size_l_product_size_m_product_size_one_size_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='size_l',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size_m',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size_one_size',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size_s',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size_xl',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size_xs',
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.CharField(blank=True, choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('One Size', 'One Size')], help_text='Выберите доступные размеры', max_length=255, verbose_name='Размеры'),
        ),
    ]
