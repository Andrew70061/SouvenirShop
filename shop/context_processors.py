from .models import ProductCategory
from django import template
from .models import Order
from django.utils import timezone


#Категории
def categories(request):
    return {'categories': ProductCategory.objects.all()}

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


#Статистика по заказам на начальной странице на действующую дату
def order_stats(request):
    today = timezone.now().date()
    new_orders_count = Order.objects.filter(status=Order.STATUS_NEW, created__date=today).count()
    cancelled_orders_count = Order.objects.filter(status=Order.STATUS_CANCELLED, created__date=today).count()
    completed_orders_count = Order.objects.filter(status=Order.STATUS_COMPLETED, created__date=today).count()

    return {
        'new_orders_count': new_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'completed_orders_count': completed_orders_count,
    }