from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = {
        ('new', 'новый'),
        ('accept', 'принят'),
        ('work', 'готовят'),
        ('delivery', 'доставка'),
        ('completed', 'завершён'),
    }
    PAYMENT_METHODS = {
        ('cash', 'наличные'),
        ('card', 'карта'),
    }

    firstname = models.CharField(verbose_name='Имя', max_length=100)
    lastname = models.CharField(verbose_name='Фамилия', max_length=100, blank=True)
    phonenumber = PhoneNumberField(region='RU', verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес')
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    status = models.CharField(
        choices=ORDER_STATUS_CHOICES,
        default='new',
        max_length=10,
        db_index=True,
        verbose_name='Статус',
    )
    payment_method = models.CharField(
        choices=PAYMENT_METHODS,
        max_length=10,
        db_index=True,
        verbose_name='Способ оплаты'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='restaurants',
        null=True,
        blank=True,
        verbose_name='Ресторан',
    )
    creation = models.DateTimeField(verbose_name='Создание заказа', auto_now_add=True, db_index=True)
    time_accept = models.DateTimeField(verbose_name='Заказ принят', null=True, blank=True)
    time_work = models.DateTimeField(verbose_name='Готовка заказа', null=True, blank=True)
    time_delivery = models.DateTimeField(verbose_name='Доставка заказа', null=True, blank=True)
    time_completed = models.DateTimeField(verbose_name='Заказ выполнен', null=True, blank=True)

    def status_update(self):
        self.status = 'work'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id}'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product', verbose_name='Продукт',)
    quantity = models.IntegerField(verbose_name='Количество', validators=[MinValueValidator(1)])
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Детали заказа'
        verbose_name_plural = 'Детали заказа'

    def __str__(self):
        return f'{self.products}'

