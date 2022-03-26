from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.auth.models import User

from django.db import models


class Supplier(models.Model):
    """представляет поставщика товара"""
    name = models.CharField(
        max_length=100,
        unique=False,
        verbose_name='юридическое название'
    )
    inn = models.CharField(
        max_length=200,
        unique=False,
        null=True,
        verbose_name='ИНН'
    )
    ogrn = models.CharField(
        max_length=200,
        unique=False,
        null=True,
        verbose_name='ОГРН'
    )
    address = models.CharField(
        max_length=200,
        unique=False,
        verbose_name='адрес'
    )
    contact_person = models.CharField(
        max_length=200,
        unique=False,
        verbose_name='контактное лицо'
    )
    telephone = models.CharField(
        max_length=200,
        unique=False,
        verbose_name='телефон'
    )
    email = models.EmailField(
        max_length=100,
        unique=False,
        verbose_name='почта'
    )
    is_actual = models.BooleanField(
        default=True,
        verbose_name='действующий'
    )

    class Meta:
        verbose_name = 'Поставщика'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name


class Supply(models.Model):
    """представляет заказ на поставку товара"""
    STATUS_list = (
        ('создана', 'создана'),
        ('заказана', 'заказана'),
        ('поступила', 'поступила на склад')
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        null=False,
        verbose_name='время создания'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_list,
        null=False,
        verbose_name='статус'
    )
    quantity = models.IntegerField(
        verbose_name='кол-во',
        null=False)
    good = models.ForeignKey(
        'Good',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='товар'
    )
    supplier = models.ForeignKey(
        'Supplier',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='поставщик'
    )
    order = models.ForeignKey(
        'Order',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='номер заказа'
    )

    class Meta:
        verbose_name = 'Поставку'
        verbose_name_plural = 'Поставки'


class Good(models.Model):
    """представляет товар"""
    UNITS = (
        ('кг', 'килограммы'),
        ('шт', 'штуки')
    )
    title = models.CharField(max_length=100, verbose_name='название')
    category = TreeForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='goods',
        null=False,
        verbose_name='категория'
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='цена')
    quantity = models.IntegerField(verbose_name='кол-во на складе', null=True)
    unit = models.CharField(
        max_length=2,
        choices=UNITS,
        null=False,
        verbose_name='ед. измерения'
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='время создания'
    )
    available_for_order = models.BooleanField(
        default=True,
        verbose_name='продается')
    artikul = models.CharField(max_length=100, verbose_name='артикул')
    suppliers = models.ManyToManyField(Supplier)
    purchase_prices = models.ForeignKey(
        'PurchasePrice',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='закупочные цены'
    )

    class Meta:
        verbose_name = 'Товары'
        verbose_name_plural = 'Товары'
        ordering = ['title']

    def __str__(self):
        return self.title


class PurchasePrice(models.Model):
    """представляет закупочную цену товара"""
    purchase_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='цена закупа'
    )
    supplier = models.OneToOneField(
        'Supplier',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='id_пользователя'
    )


class Category(MPTTModel):
    """представляет категорию товара"""
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='родительская категория'
    )

    class Meta:
        verbose_name = 'Категории товаров'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name

    def get_goods(self):
        """
        возвращает все товары, соответствующие
        данному экземпляру сласса Category
        :return: QuerySet
        """
        goods = Good.objects.filter(category=self.id)
        return goods


class Order(models.Model):
    """представляет заказ товара покупателем"""
    STATUS_list = (
        ('создан', 'создан'),
        ('заказан', 'заказан'),
        ('собран', 'собран'),
        ('исполнен', 'исполнен'),
        ('отменен', 'отменен')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_list,
        null=False,
        verbose_name='статус'
    )
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.PROTECT,
        verbose_name='заказы'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Клиентские заказы'















