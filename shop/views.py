from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem
from .forms import CustomUserCreationForm, ProfileEditForm, RemoveFromCartForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse


#Основная страница
def index(request):
    products = Product.objects.filter(publish=True)
    categories = ProductCategory.objects.all()
    return render(request, 'index.html', {'products': products, 'categories': categories})


#Поиск товаров
def search(request):
    query = request.GET.get('q')
    if query:
        search_results = Product.objects.filter(title__icontains=query) | Product.objects.filter(description__icontains=query)
    else:
        search_results = Product.objects.none()
    categories = ProductCategory.objects.all()
    return render(request, 'search_results.html', {'search_results': search_results, 'categories': categories})


#Категории товаров
def category_detail(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products = Product.objects.filter(category=category, publish=True)
    categories = ProductCategory.objects.all()
    return render(request, 'category_detail.html', {'category': category, 'products': products, 'categories': categories})


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
        product.total_price = product.price * cart_items.get(str(product.id), 0)

    total_price = sum(product.total_price for product in products)

    return render(request, 'cart.html', {'cart_items': cart_items, 'products': products, 'total_price': total_price})


#Удаление товара из корзины
def remove_from_cart(request, product_id):
    if 'cart' in request.session:
        if str(product_id) in request.session['cart']:
            del request.session['cart'][str(product_id)]
            request.session.modified = True
    return redirect('shop:view_cart')


#Оформление заказа
@login_required
def checkout(request):
    if request.method == 'POST':
        #Получение данных формы оформления заказа для bd
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
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