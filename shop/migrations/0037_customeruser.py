# Generated by Django 5.1b1 on 2024-09-16 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0036_remove_orderitem_size_alter_orderitem_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='Имя пользователя')),
                ('password', models.CharField(max_length=128, verbose_name='Пароль')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Покупатель',
                'verbose_name_plural': 'Покупатели',
            },
        ),
    ]
