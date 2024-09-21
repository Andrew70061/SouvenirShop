from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib import admin
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError



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
    quantity = models.IntegerField(verbose_name='Количество товара', default=0, null=True)


    #Информация о поставщике товара
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
        return f'{self.title} / Цена: {self.price} / Количество на складе: {self.quantity}'

#Фото товара
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m', verbose_name='Изображение')
    alt = models.CharField(max_length=255, verbose_name='Текст вместо изображения', blank=True)
    order = models.PositiveIntegerField(verbose_name='Порядок сортировки', null=True, default=0, blank=True)
    class Meta:
        verbose_name = 'изображение товара'
        verbose_name_plural = 'Изображения товаров'



#Создание категорий
class ProductCategory(MPTTModel):
    title = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=150, verbose_name='slug', unique=True)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name='Родительская категория')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = 'категорию'
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

#Поставки
class Supply(models.Model):
    id_supply = models.PositiveIntegerField(verbose_name='Номер поставки', unique=True)
    supplier = models.ForeignKey(Supplier, verbose_name='Поставщик', on_delete=models.CASCADE)
    responsible = models.ForeignKey(User, verbose_name='Ответственный', on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    act_number = models.CharField(max_length=5, verbose_name='Номер акта приема-передачи')
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'

    def __str__(self):
        return f'Поставка №{self.id_supply}'

@receiver(pre_save, sender=Supply)
def set_supply_number(sender, instance, **kwargs):
    if not instance.id_supply:
        #Получение последнего номера поставки
        last_supply = Supply.objects.order_by('-id_supply').first()
        if last_supply:
            instance.id_supply = last_supply.id_supply + 1
        else:
            instance.id_supply = 1
    #Проверка номера поставки на уникальность номера поставки
    if Supply.objects.filter(id_supply=instance.id_supply).exclude(pk=instance.pk).exists():
        raise ValidationError(f'{instance.id_supply} ')


#Товар в поставке
class SupplyItem(models.Model):
    supply = models.ForeignKey(Supply, verbose_name='Поставка', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Товар в поставке'
        verbose_name_plural = 'Товары в поставке'

    def __str__(self):
        return f'{self.product.title} ({self.quantity})'

@receiver(post_save, sender=SupplyItem)
def update_product_quantity(sender, instance, **kwargs):
    #Прибавление остатка товара
    instance.product.quantity += instance.quantity
    instance.product.save()


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
    user = models.ForeignKey(User, verbose_name='Покупатель', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'is_staff': False})
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
        return 'Заказ {}'.format(self.id)


#Выбор товара в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)
    price = models.DecimalField(verbose_name='Цена', max_digits=20, decimal_places=2)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары из заказа'

    #Отображение артикула при выборе товара
    def __str__(self):
        return f'Артикул: {self.product.sku}'

    #Проверка остатков товара и цены при создании заказа
    def clean(self):
        if self.product and self.quantity > self.product.quantity:
            raise ValidationError(f'Количество товара в заказе превышает количество на складе. Доступно: {self.product.quantity}')

        if self.product and self.price != self.product.price:
            raise ValidationError(f'Цена товара в заказе отличается от цены товара. Цена на товара: {self.product.price}')

    #Вычисление итоговой цены по количеству товара
    @admin.display(description='Итого')
    def get_cost(self):
        return self.price * self.quantity if self.price is not None and self.quantity is not None else 0

    def save(self, *args, **kwargs):
        #Вычитание количества остатков заказанного товара из бд
        self.product.quantity -= self.quantity
        self.product.save(update_fields=['quantity'])

        super().save(*args, **kwargs)


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


#Платежи
class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id}"


#Отчеты
class Report(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название отчета', editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Выгрузку отчета по заказам'
        verbose_name_plural = 'Отчеты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:  # Проверяем, что это новый объект
            self.name = "Отчет по заказам"
        super().save(*args, **kwargs)