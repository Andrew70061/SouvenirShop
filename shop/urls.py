from django.urls import path
from .views import (index, search, category_detail, about, contact, register,
profile, orders, edit_profile, add_to_cart, view_cart, checkout, remove_from_cart, update_quantity)
from django.contrib.auth import views as auth_views

app_name = 'shop'

urlpatterns = [
    path('', index, name='index'),
    path('search/', search, name='search'),
    path('category/<slug:slug>/', category_detail, name='product-by-category'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/', profile, name='profile'),
    path('orders/', orders, name='orders'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update_quantity/<int:product_id>/', update_quantity, name='update_quantity'),
]