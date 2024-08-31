from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem, Brand
from .forms import CustomUserCreationForm, ProfileEditForm, RemoveFromCartForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q, Min, Max


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

    # Фильтрация по цене при поиске товаров
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        search_results = search_results.filter(price__gte=price_min)
    if price_max:
        search_results = search_results.filter(price__lte=price_max)

    # Фильтрация по категориям при поиске товаров
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        search_results = search_results.filter(category__id__in=selected_categories)

    # Фильтрация по брендам при поиске товаров
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        search_results = search_results.filter(brand__id__in=selected_brands)

    # Фильтрация по названию при поиске товаров
    name = request.GET.get('name')
    if name:
        search_results = search_results.filter(Q(title__icontains=name) | Q(description__icontains=name))

    # Фильтрация по количеству при поиске товаров
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        search_results = search_results.filter(quantity__gte=quantity_min)
    if quantity_max:
        search_results = search_results.filter(quantity__lte=quantity_max)

    # Обработка сортировки при поиске товаров
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            search_results = search_results.order_by(sort_by)
        else:
            search_results = search_results.order_by(f'-{sort_by}')

    # Пагинация
    paginator = Paginator(search_results, per_page)
    page = request.GET.get('page')
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    # Минимальная и максимальная цена при поиске товаров
    min_price = Product.objects.aggregate(Min('price'))['price__min']
    max_price = Product.objects.aggregate(Max('price'))['price__max']

    # Минимальное и максимальное количество при поиске товаров
    min_quantity = Product.objects.aggregate(Min('quantity'))['quantity__min']
    max_quantity = Product.objects.aggregate(Max('quantity'))['quantity__max']

    # Список брендов при поиске товаров
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

    # Фильтрация по цене на странице с категориями
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Фильтрация по категориям
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    # Фильтрация по брендам на странице с категориями
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)

    # Фильтрация по названию на странице с категориями
    name = request.GET.get('name')
    if name:
        products = products.filter(Q(title__icontains=name) | Q(description__icontains=name))

    # Фильтрация по количеству на странице с категориями
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        products = products.filter(quantity__gte=quantity_min)
    if quantity_max:
        products = products.filter(quantity__lte=quantity_max)

    # Обработка сортировки на странице с категориями
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')

    # Пагинация
    paginator = Paginator(products, per_page)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Минимальная и максимальная цены на странице с категориями
    min_price = Product.objects.aggregate(Min('price'))['price__min']
    max_price = Product.objects.aggregate(Max('price'))['price__max']

    # Минимальное и максимальное количество на странице с категориями
    min_quantity = Product.objects.aggregate(Min('quantity'))['quantity__min']
    max_quantity = Product.objects.aggregate(Max('quantity'))['quantity__max']

    # Список брендов на странице с категориями
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


#Товары и фильтры(index)
def index(request):
    per_page_str = request.GET.get('per_page', '10')
    if not per_page_str:
        per_page_str = '10'
    per_page = int(per_page_str)

    products = Product.objects.filter(publish=True)
    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()

    # Фильтрация по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Фильтрация по категориям
    category_ids = request.GET.getlist('category')
    if category_ids:
        products = products.filter(category__id__in=category_ids)

    # Фильтрация по брендам
    brand_ids = request.GET.getlist('brand')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)

    # Фильтрация по названию
    name = request.GET.get('name')
    if name:
        products = products.filter(Q(title__icontains=name) | Q(description__icontains=name))

    # Фильтрация по количеству
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if quantity_min:
        products = products.filter(quantity__gte=quantity_min)
    if quantity_max:
        products = products.filter(quantity__lte=quantity_max)

    # Обработка сортировки
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')  # По умолчанию сортировка по возрастанию

    if sort_by:
        if sort_by == 'name':
            sort_by = 'title'  # Заменяем 'name' на 'title'
        if sort_order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')

    # Пагинация
    paginator = Paginator(products, per_page)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Минимальная и максимальная цены из базы данных
    price_range = Product.objects.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price = price_range['min_price'] or 0
    max_price = price_range['max_price'] or 1000

    # Минимальная и максимальная количество из базы данных
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


#Заказы пользователя
@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': user_orders})


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


#Просмотр корзины
def view_cart(request):
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())

    for product in products:
        product.quantity_in_cart = cart_items.get(str(product.id), 0)
        product.total_price = product.price * product.quantity_in_cart

    total_price = sum(product.total_price for product in products)

    return render(request, 'cart.html', {'cart_items': cart_items, 'products': products, 'total_price': total_price})


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
    if request.method == 'POST':
        #Получение данных формы оформления заказа для bd
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        comment = request.POST.get('comment')

        #Создание заказа в bd
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city,
            comment=comment
        )

        #Получение id товара для заказа в bd
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        #Очистка корзины после оформления
        request.session['cart'] = {}

        return redirect(reverse('shop:orders'))

    return render(request, 'checkout.html')