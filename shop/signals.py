from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .telegram_bot import send_telegram_message

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    if created:
        message = f"Новый заказ №{instance.id} от {instance.created}"
        send_telegram_message(message)