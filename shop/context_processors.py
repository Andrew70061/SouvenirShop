from .models import ProductCategory
from django import template
from .models import Order
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import io
import base64
import matplotlib.pyplot as plt


#Категории
def categories(request):
    return {'categories': ProductCategory.objects.all()}

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


#Статистика по заказам на начальной странице: на действующую дату и за 30 дней в гистограмме
def order_stats(request):
    today = timezone.now().date()
    new_orders_count = Order.objects.filter(status=Order.STATUS_NEW, created__date=today).count()
    cancelled_orders_count = Order.objects.filter(status=Order.STATUS_CANCELLED, created__date=today).count()
    completed_orders_count = Order.objects.filter(status=Order.STATUS_COMPLETED, created__date=today).count()

    #Гистограмма заказов за месяц
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    orders_per_day = Order.objects.filter(created__range=(start_date, end_date)).values('created__date').annotate(count=Count('id'))

    dates = [order['created__date'] for order in orders_per_day]
    counts = [order['count'] for order in orders_per_day]

    plt.figure(figsize=(10, 5))
    plt.bar(dates, counts, color='#8c1d2f')
    plt.xlabel('Дата')
    plt.ylabel('Количество заказов')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())
    plt.xticks(rotation=0)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return {
        'new_orders_count': new_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'completed_orders_count': completed_orders_count,
        'orders_chart': image_base64,
    }