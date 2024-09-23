from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from shop.models import Product, ProductCategory, ProductImages, Supplier, Order, OrderItem, Brand, SupplyItem,Supply, Report, Feedback
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
import csv
import pandas as pd
from datetime import datetime, timezone


#Поставщики и поставки
class SupplierAdmin(admin.ModelAdmin):
    search_fields = [ 'name', 'first_name', 'last_name', 'email', 'phone']

class SupplyItemInline(admin.TabularInline):
    model = SupplyItem
    extra = 1

class SupplyAdmin(admin.ModelAdmin):
    inlines = [SupplyItemInline]
    list_display = ['id_supply','supplier', 'responsible', 'act_number']
    search_fields = ['number', 'supplier__name', 'responsible__username', 'act_number']
    list_filter = ['supplier__name','responsible']

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Supply, SupplyAdmin)


#Картинки для товаров
class ProductImagesAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProductImages, ProductImagesAdmin)


#Товар
class ProductAdminInline(admin.TabularInline):
    model = ProductImages
    extra = 0

#Категории
class ProductCategoryAdmin(MPTTModelAdmin):
    list_display = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['parent']
    search_fields = ['title', 'slug']

admin.site.register(ProductCategory, ProductCategoryAdmin)


#Бренды
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

admin.site.register(Brand, BrandAdmin)


#Список товаров
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku','title', 'category','price', 'quantity', 'publish', 'created', 'updated']
    list_filter = ('category', 'brand', 'publish')
    list_editable = ['price','quantity', 'publish']
    search_fields = ('title', 'category__title', 'sku', 'brand__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductAdminInline]

admin.site.register(Product, ProductAdmin)


#Выбор товара в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    ForeignKey = ['product']
    readonly_fields = ('get_cost',)


#Фильтр по статусам заказов
class StatusFilter(admin.SimpleListFilter):
    title = 'Статус заказа'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Order.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


#Заказ и поиск по заказам
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address',
                    'postal_code', 'city', 'paid', 'created', 'updated', 'status']
    list_filter = ['paid', 'created', 'updated', StatusFilter]
    search_fields = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city','status']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)


#Пользователи
class IsStaffFilter(admin.SimpleListFilter):
    title = 'Статус'
    parameter_name = 'is_staff'

    def lookups(self, request, model_admin):
        return (
            ('Сотрудник', 'Сотрудник'),
            ('Покупатель', 'Покупатель'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Сотрудник':
            return queryset.filter(is_staff=True)
        if self.value() == 'Покупатель':
            return queryset.filter(is_staff=False)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_is_staff_display','date_joined','last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_superuser','is_active', IsStaffFilter)

    def get_is_staff_display(self, obj):
        return 'Сотрудник' if obj.is_staff else 'Покупатель'
    get_is_staff_display.short_description = 'Статус'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


#Отчеты
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    actions = ['export_orders_csv', 'export_orders_excel']

    def save_model(self, request, obj, form, change):
        obj.name = "Отчет по заказам"
        super().save_model(request, obj, form, change)

    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Имя', 'Фамилия', 'Телефон', 'Email', 'Адрес', 'Индекс', 'Город', 'Комментарий', 'Дата создания', 'Оплачено', 'Статус'])

        orders = Order.objects.all().values_list('id', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'postal_code', 'city', 'comment', 'created', 'paid', 'status')
        for order in orders:
            writer.writerow(order)

        return response
    export_orders_csv.short_description = 'Выгрузить заказы в CSV'

    def export_orders_excel(self, request, queryset):
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
            'Дата создания': [order.created.astimezone(timezone.utc).replace(tzinfo=None) for order in orders],
            'Оплачено': [order.paid for order in orders],
            'Статус': [order.status for order in orders],
        }

        df = pd.DataFrame(data)
        df.to_excel(response, index=False)

        return response
    export_orders_excel.short_description = 'Выгрузить заказы в Excel'

admin.site.register(Report, ReportAdmin)


#Обращение покупателей
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

admin.site.register(Feedback, FeedbackAdmin)


#Название в панели навигации
admin.site.site_header = 'Управление Souvenir Muiv Shop'
