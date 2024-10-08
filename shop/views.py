from django.shortcuts import render, get_object_or_404, redirect
from payments import get_payment_model, RedirectNeeded, PaymentStatus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from .models import Product, ProductCategory, Order, OrderItem, Brand, Report
import csv
import pandas as pd
from .forms import CustomUserCreationForm, ProfileEditForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Q, Min, Max
import asyncio
from .telegram_bot import send_telegram_message
from .forms import FeedbackForm


#===========================================Сайт_интернет-магазина_SouvenirShop========================================#

#Поиск на сайте
def search(request):
    query = request.GET.get('q')
    per_page_str = request.GET.get('per_page', '10')
    if not per_page_str:
        per_page_str = '10'
    per_page = int(per_page_str)

    if query:
        search_results = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    else:
        search_results = Product.objects.none()

    categories = ProductCategory.objects.all()

    #Фильтрация по цене при поиске товаров
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        search_results = search_results.filter(price__gte=price_min)
    if price_max:
        search_results = search_results.filter(price__lte=price_max)

    #Фильтрация по категориям при поиске товаров
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        search_results = search_results.filter(category__id__in=selected_categories)

    #Фильтрация по брендам при поиске товаров
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        search_results = search_results.filter(brand__id__in=selected_brands)

    #Фильтрация по названию при поиске товаров
    name = request.GET.get('name')
    if name:
        search_results = search_results.filter(Q(title__icontains=name) | Q(description__icontains=name))

    #Фильтрация по количеству при поиске товаров
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        search_results = search_results.filter(quantity__gte=quantity_min)
    if quantity_max:
        search_results = search_results.filter(quantity__lte=quantity_max)

    #Обработка сортировки при поиске товаров
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            search_results = search_results.order_by(sort_by)
        else:
            search_results = search_results.order_by(f'-{sort_by}')

    #Страницы
    paginator = Paginator(search_results, per_page)
    page = request.GET.get('page')
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    #Минимальная и максимальная цена при поиске товаров
    min_price = Product.objects.aggregate(Min('price'))['price__min']
    max_price = Product.objects.aggregate(Max('price'))['price__max']

    #Минимальное и максимальное количество при поиске товаров
    min_quantity = Product.objects.aggregate(Min('quantity'))['quantity__min']
    max_quantity = Product.objects.aggregate(Max('quantity'))['quantity__max']

    #Список брендов при поиске товаров для фильтра
    brands = Brand.objects.all()

    context = {
        'search_results': search_results,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
        'min_quantity': min_quantity,
        'max_quantity': max_quantity,
        'brands': brands,
    }

    return render(request, 'search_results.html', context)


#Категории товаров
def category_detail(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    per_page_str = request.GET.get('per_page', '10')
    if not per_page_str:
        per_page_str = '10'
    per_page = int(per_page_str)

    products = Product.objects.filter(category=category, publish=True)
    categories = ProductCategory.objects.all()

    #Фильтрация по цене на странице с категориями
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    #Фильтрация по категориям
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    #Фильтрация по брендам на странице с категориями
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)

    #Фильтрация по названию на странице с категориями
    name = request.GET.get('name')
    if name:
        products = products.filter(Q(title__icontains=name) | Q(description__icontains=name))

    #Фильтрация по количеству на странице с категориями
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        products = products.filter(quantity__gte=quantity_min)
    if quantity_max:
        products = products.filter(quantity__lte=quantity_max)

    #Обработка сортировки на странице с категориями
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')

    #Страницы
    paginator = Paginator(products, per_page)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    #Минимальная и максимальная цены на странице с категориями
    min_price = Product.objects.aggregate(Min('price'))['price__min']
    max_price = Product.objects.aggregate(Max('price'))['price__max']

    #Минимальное и максимальное количество на странице с категориями
    min_quantity = Product.objects.aggregate(Min('quantity'))['quantity__min']
    max_quantity = Product.objects.aggregate(Max('quantity'))['quantity__max']

    #Список брендов на странице с категориями
    brands = Brand.objects.all()

    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
        'min_quantity': min_quantity,
        'max_quantity': max_quantity,
        'brands': brands,
    }

    return render(request, 'category_detail.html', context)


#Страница товары
def index(request):
    per_page_str = request.GET.get('per_page', '10')
    if not per_page_str:
        per_page_str = '10'
    per_page = int(per_page_str)

    products = Product.objects.filter(publish=True)
    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()

    #Фильтрация по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    #Фильтрация по категориям
    category_ids = request.GET.getlist('category')
    if category_ids:
        products = products.filter(category__id__in=category_ids)

    #Фильтрация по брендам
    brand_ids = request.GET.getlist('brand')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)

    #Фильтрация по названию
    name = request.GET.get('name')
    if name:
        products = products.filter(Q(title__icontains=name) | Q(description__icontains=name))

    #Фильтрация по количеству
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        products = products.filter(quantity__gte=quantity_min)
    if quantity_max:
        products = products.filter(quantity__lte=quantity_max)

    #Обработка сортировки
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')  # По умолчанию сортировка по возрастанию

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')

    #Страницы с товарами
    paginator = Paginator(products, per_page)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    #Минимальная и максимальная цены из базы данных
    price_range = Product.objects.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price = price_range['min_price'] or 0
    max_price = price_range['max_price'] or 1000

    #Минимальная и максимальная количество из базы данных
    quantity_range = Product.objects.aggregate(min_quantity=Min('quantity'), max_quantity=Max('quantity'))
    min_quantity = quantity_range['min_quantity'] or 0
    max_quantity = quantity_range['max_quantity'] or 10000

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'min_price': min_price,
        'max_price': max_price,
        'min_quantity': min_quantity,
        'max_quantity': max_quantity,
    }

    return render(request, 'index.html', context)


#Страница каждого товара
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


#Страница о нас
def about(request):
    categories = ProductCategory.objects.all()
    return render(request, 'about.html', {'categories': categories})


#Страница контакты
def contact(request):
    categories = ProductCategory.objects.all()
    return render(request, 'contact.html', {'categories': categories})


#Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration_register.html', {'form': form})


#Вход пользователя
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Неправильное имя пользователя или пароль.')
        else:
            messages.error(request, 'Неправильное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


#Профиль пользователя
@login_required
def profile(request):
    return render(request, 'profile.html')


#Заказы покупателя
@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user)
    for order in user_orders:
        order.is_paid = order.paid
        if order.self_pickup:
            order.delivery_method = 'Самовывоз'
        elif order.courier_delivery:
            order.delivery_method = 'Доставка курьером'
        else:
            order.delivery_method = 'Не указан'
    return render(request, 'orders.html', {'orders': user_orders})


#Отмена заказов покупателем
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == order.STATUS_DELIVERS:
        messages.error(request, 'Ваш заказ уже у курьера, свяжитесь с ними для отмены:8-916-839-00-01 .')
    elif order.status != order.STATUS_CANCELLED:
        order.status = order.STATUS_CANCELLED
        order.save()

        #Возвращаем остаток товаров при отмене
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            product = item.product
            product.quantity += item.quantity
            product.save()

        messages.success(request, 'Заказ успешно отменен.')

        #Отправка уведомления в Telegram
        message = (
            f"Покупатель отменил заказ №{order.id}\n"
            f"Товары в заказе:\n"
        )
        for item in order_items:
            message += f"- {item.product.title} (x{item.quantity}): {item.price} руб.\n"

        message += "Остаток возвращен на склад, проверьте."

        asyncio.run(send_telegram_message(message))

    return redirect('shop:orders')


#Редактирование профиля пользователя
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('shop:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    categories = ProductCategory.objects.all()
    return render(request, 'edit_profile.html', {'form': form, 'categories': categories})


#Добавление товара в корзину
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if 'cart' not in request.session:
        request.session['cart'] = {}
    request.session['cart'][product_id] = request.session['cart'].get(product_id, 0) + 1
    request.session.modified = True
    return redirect('index')


#Добавление доставки в корзине
def add_delivery_to_cart(request):
    if request.method == 'POST':
        self_pickup = request.POST.get('self_pickup') == 'True'
        courier_delivery = request.POST.get('courier_delivery') == 'True'

        if self_pickup:
            delivery_product = get_object_or_404(Product, id=16)
            if 'cart' in request.session and 16 in request.session['cart']:
                del request.session['cart'][16]
                request.session.modified = True

        #Добавление доставки в корзину
        if courier_delivery:
            delivery_product = get_object_or_404(Product, id=16)
            if 'cart' not in request.session:
                request.session['cart'] = {}
            request.session['cart'][16] = request.session['cart'].get(16, 0) + 1
            request.session.modified = True

        #Сохранение выбранного способа доставки в сессию
        if self_pickup:
            request.session['delivery_method'] = 'self_pickup'
        elif courier_delivery:
            request.session['delivery_method'] = 'courier_delivery'
        else:
            request.session['delivery_method'] = None

    return redirect('shop:view_cart')


#Просмотр корзины
def view_cart(request):
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())

    for product in products:
        product.quantity_in_cart = cart_items.get(str(product.id), 0)
        product.total_price = product.price * product.quantity_in_cart

    total_price = sum(product.total_price for product in products)

    delivery_method = request.session.get('delivery_method', 'self_pickup')  # По умолчанию самовывоз

    return render(request, 'cart.html', {'products': products, 'total_price': total_price, 'delivery_method': delivery_method})


#Удаление товара из корзины
def remove_from_cart(request, product_id):
    if 'cart' in request.session:
        if str(product_id) in request.session['cart']:
            del request.session['cart'][str(product_id)]
            request.session.modified = True
    return redirect('shop:view_cart')


#Изменение количества товара в корзине
def update_quantity(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = request.POST.get('quantity')
        if 'cart' in request.session:
            cart = request.session['cart']
            if str(product_id) in cart:
                product = Product.objects.get(id=product_id)
                if action == 'increase':
                    if cart[str(product_id)] < product.quantity:
                        cart[str(product_id)] += 1
                elif action == 'decrease' and cart[str(product_id)] > 1:
                    cart[str(product_id)] -= 1
                elif quantity:
                    try:
                        quantity = int(quantity)
                        if quantity > 0 and quantity <= product.quantity:
                            cart[str(product_id)] = quantity
                        else:
                            cart[str(product_id)] = product.quantity
                    except ValueError:
                        pass
                request.session.modified = True
    return redirect('shop:view_cart')


#Оформление заказа
@login_required
def checkout(request):
    delivery_method = request.session.get('delivery_method', 'self_pickup')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        comment = request.POST.get('comment')
        self_pickup = delivery_method == 'self_pickup'
        courier_delivery = delivery_method == 'courier_delivery'
        pay_online = request.POST.get('pay_online') == 'on'
        pay_on_delivery = request.POST.get('pay_on_delivery') == 'on'

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city,
            comment=comment,
            self_pickup=self_pickup,
            courier_delivery=courier_delivery,
            paid=pay_online
        )

        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(order=order, product=product, price=product.price, quantity=quantity)

        #Очистка корзины
        request.session['cart'] = {}

        #Отправка уведомления в Telegram
        message = (
            f"Новый заказ №{order.id} от {order.created}\n"
            f"Имя: {order.first_name} {order.last_name}\n"
            f"Телефон: {order.phone_number}\n"
            f"Email: {order.email}\n"
            f"Адрес: {order.address}, {order.postal_code}, {order.city}\n"
            f"Комментарий: {order.comment}\n"
            f"Способ доставки: {'Самовывоз' if order.self_pickup else 'Доставка курьером'}\n"
            f"Оплачено: {'Да' if order.paid else 'Нет'}\n"
            f"Товары в заказе:\n"
        )
        for item in OrderItem.objects.filter(order=order):
            message += f"- {item.product.title} (x{item.quantity}): {item.price} руб.\n"

        asyncio.run(send_telegram_message(message))

        if pay_online:
            return redirect(reverse('shop:orders'))
        elif pay_on_delivery:
            return redirect(reverse('shop:orders'))
        else:
            return redirect(reverse('shop:orders'))

    return render(request, 'checkout.html')


#Заказ в 1 клик
@csrf_exempt
def buy_one_click(request):
    if request.method == 'POST':
        #Получение данных формы оформления заказа для бд
        name = request.POST.get('name')
        phone_number = request.POST.get('phone')
        comment = request.POST.get('comment')
        product_id = request.POST.get('product_id')

        #Проверка наличия товара
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return render(request, 'error.html', {'message': 'Product not found'})

        #Создание заказа в bd
        order = Order.objects.create(
            first_name=name,
            phone_number=phone_number,
            comment= comment
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        #Отправка уведомления в Telegram
        message = (
            f"Новый заказ в 1 клик №{order.id} от {order.created}\n"
            f"Имя: {order.first_name}\n"
            f"Телефон: {order.phone_number}\n"
            f"Комментарий: {order.comment}\n"
            f"Товар: {product.title}\n"
            f"Цена: {product.price} руб.\n"
            f"Пожалуйста, свяжитесь с покупателем для подтверждения заказа."
        )
        asyncio.run(send_telegram_message(message))

        return redirect(reverse('shop:index'))
    else:
        return render(request, 'error.html', {'message': 'Method not allowed'})


#Создание платежа
def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    Payment = get_payment_model()
    payment = Payment.objects.create(
        variant='default',
        currency='RUB',
        description=f'Order #{order.id}'
    )
    try:
        return redirect(payment.get_process_url())
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))


#Обработка платежа
def payment_success(request, payment_id):
    payment = get_object_or_404(get_payment_model(), id=payment_id)
    if payment.status == PaymentStatus.CONFIRMED:
        order_id = payment.description.split('#')[1]
        order = get_object_or_404(Order, id=order_id)
        order.paid = True
        order.save()
        return render(request, 'payment_success.html')
    return render(request, 'payment_failure.html')

#Форма обратной связи
@csrf_exempt
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()

            #Отправка уведомления в Telegram
            message = (
                f"Новое обращение покупателя №{feedback.id} от {feedback.created_at}\n"
                f"Имя: {feedback.name}\n"
                f"Email: {feedback.email}\n"
                f"Сообщение: {feedback.message}\n"
                f"Пожалуйста, проверьте сообщение и ответьте покупателю."
            )
            asyncio.run(send_telegram_message(message))

            return redirect(reverse('shop:feedback_success'))
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})

def feedback_success_view(request):
    return render(request, 'feedback_success.html')


#===========================================Сайт_интернет-магазина_SouvenirShop========================================#


#===========================================Веб-приложение_SouvenirShopMUIV============================================#
#Выгрузка отчета
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Имя', 'Фамилия', 'Телефон', 'Email', 'Адрес', 'Индекс', 'Город', 'Комментарий', 'Дата создания', 'Оплачено'])

    orders = Order.objects.all().values_list('id', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'postal_code', 'city', 'comment', 'created', 'paid')
    for order in orders:
        writer.writerow(order)

    return response

def export_orders_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'

    orders = Order.objects.all()
    data = {
        'ID': [order.id for order in orders],
        'Имя': [order.first_name for order in orders],
        'Фамилия': [order.last_name for order in orders],
        'Телефон': [order.phone_number for order in orders],
        'Email': [order.email for order in orders],
        'Адрес': [order.address for order in orders],
        'Индекс': [order.postal_code for order in orders],
        'Город': [order.city for order in orders],
        'Комментарий': [order.comment for order in orders],
        'Дата создания': [order.created for order in orders],
        'Оплачено': [order.paid for order in orders],
    }

    df = pd.DataFrame(data)
    df.to_excel(response, index=False)

    return response



#===========================================Веб-приложение_SouvenirShopMUIV============================================#