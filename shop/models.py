from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator


#Создание товары
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название товара')
    slug = models.SlugField(max_length=150, verbose_name='slug', unique=True)
    description = models.TextField(verbose_name='Описание товара')
    category = TreeForeignKey('ProductCategory', on_delete=models.PROTECT, default=1,
                              related_name='products', verbose_name='Категория')


    #Мета
    sku = models.CharField(max_length=255, verbose_name='Артикул')
    barcode = models.CharField(verbose_name='Штрихкод', max_length=255, blank=True)
    manufacturer_countries = models.CharField(max_length=255, verbose_name='Страна-производитель', blank=True)
    brand = models.ForeignKey('Brand', verbose_name='Бренд', on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.CharField(max_length=255, verbose_name='Производитель', blank=True)
    vendor_code = models.CharField(max_length=255, verbose_name='Партномер', blank=True)


    #Габариты
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Длина (см.)', null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ширина (см.)', null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Высота (см.)', null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес (г.)', null=True, blank=True)


    #Цена и остатки
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Цена', default=1,
                                validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Цена со скидкой',
                                     null=True, blank=True, validators=[MinValueValidator(0)])
    quantity = models.IntegerField(verbose_name='Количество товара', default=0, null=True)


    #Информация о поставках
    supplier = models.ForeignKey('Supplier', verbose_name='Поставщик', on_delete=models.CASCADE, null=True, blank=True)
    supplier_sku = models.IntegerField(verbose_name='Артикул у поставщика', default=0, null=True)
    supplier_url = models.URLField(verbose_name='URL', blank=True)
    supplier_price = models.IntegerField(verbose_name='Цена у поставщика', default=0, null=True,
                                         validators=[MinValueValidator(0)])


    #Метка публикации
    publish = models.BooleanField(verbose_name='Опубликовано', default=True)
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, default=1)
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)


    #Добавляем поле для изображения
    image = models.ImageField(upload_to='products/', verbose_name='Изображение', null=True, blank=True)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.title} --- {self.price}'


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m', verbose_name='Изображение')
    alt = models.CharField(max_length=255, verbose_name='Текст вместо изображения', blank=True)
    order = models.PositiveIntegerField(verbose_name='Порядок сортировки', null=True, default=0, blank=True)
    class Meta:
        verbose_name = 'изображение товара'
        verbose_name_plural = 'Изображения товаров'


class ProductCategory(MPTTModel):
    title = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=150, verbose_name='slug', unique=True)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name='Родительская категория')

    supplier = models.ForeignKey('Supplier', verbose_name='Поставщик', on_delete=models.CASCADE, null=True, blank=True)


    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('shop:product-by-category', args=[str(self.slug)])

    def __str__(self):
        return self.title


#Создание поставщиков
class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    site = models.URLField(verbose_name='Сайт', blank=True)
    first_name = models.CharField(max_length=50, verbose_name='Имя', blank=True)
    last_name = models.CharField(max_length=50, verbose_name='Фамилия', blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    phone = models.CharField(max_length=50, verbose_name='Телефон', blank=True)
    address = models.CharField(max_length=250, verbose_name='Адрес', blank=True)
    comment = models.TextField(verbose_name='Примечание', blank=True)
    markup = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Наценка', null=True, blank=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return f'{self.name}'


#Создание брендов
class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название бренда')
    description = models.TextField(verbose_name='Описание бренда', blank=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name


#Заказы
class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=12, default='')
    email = models.EmailField(verbose_name='Email')
    address = models.CharField(verbose_name='Адрес', max_length=250)
    postal_code = models.CharField(verbose_name='Индекс', max_length=20)
    city = models.CharField(verbose_name='Город', max_length=100)
    comment = models.TextField(verbose_name='Комментарий', blank=True, null=True)
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)
    paid = models.BooleanField(verbose_name='Оплачено', default=False)

    #Способ доставки
    self_pickup = models.BooleanField(verbose_name='Самовывоз из магазина', default=False)
    courier_delivery = models.BooleanField(verbose_name='Доставка курьером', default=False)

    #Статусы заказов
    STATUS_NEW = 'Новый заказ'
    STATUS_PROCESSING = 'Сборка заказа'
    STATUS_DELIVERS = 'Доставляется'
    STATUS_AWAITING_ISSUE = 'Ожидает выдачи в магазине'
    STATUS_COMPLETED = 'Доставлен'
    STATUS_COMPLETED2 = 'Выдан'
    STATUS_CANCELLED = 'Отменен'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_PROCESSING, 'Сборка заказа'),
        (STATUS_DELIVERS, 'Доставляется'),
        (STATUS_AWAITING_ISSUE, 'Ожидает выдачи в магазине'),
        (STATUS_COMPLETED, 'Доставлен'),
        (STATUS_COMPLETED2, 'Выдан'),
        (STATUS_CANCELLED, 'Отменен')
    ]
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_NEW,verbose_name='Статус заказа')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

#Выбор товара в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)
    price = models.DecimalField(verbose_name='Цена', max_digits=20, decimal_places=2)
    discount = models.DecimalField(verbose_name='Цена со скидкой', max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.product} --- {self.price}'

    def get_cost(self):
        return self.price * self.quantity


#Корзина
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Корзина покупателя'
        verbose_name_plural = 'Корзины покупателей'

    def __str__(self):
        return f'Корзина для {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    def __str__(self):
        return f'{self.product.title} в корзине {self.cart.user.username}'