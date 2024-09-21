from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from shop.models import Product, ProductCategory, ProductImages, Supplier, Order, OrderItem, Brand, SupplyItem,Supply
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


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
    list_filter = ['supplier__name']

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Supply, SupplyAdmin)


#Картинки для товаров
class ProductImagesAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProductImages, ProductImagesAdmin)


#Товары
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


#Товары
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'quantity', 'publish', 'created', 'updated']
    list_filter = ['publish', 'created']
    list_editable = ['quantity', 'publish']
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
    search_fields = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)


#Пользователи
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = 'Администратирование MUIV Souvenir Shop'
