from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.auth.models import User
from django.db.models import Sum
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
        verbose_name='статус',
        default='заказана'
    )
    total_positions = models.PositiveIntegerField(
        verbose_name='кол-во позиций',
        null=False
    )
    total_purchase_price = models.DecimalField(
        null=False,
        max_digits=15,
        decimal_places=2,
        verbose_name='сумма поставки'
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

    def __str__(self):
        return str(self.id)

    def get_order_id(self):
        """возвращает номер заказа"""
        return self.order_id if self.order_id else ''


class SupplyItems(models.Model):
    """Представляет позиции поставки"""
    STATUS_list = (
        ('заказана', 'заказана'),
        ('отменена', 'отменена'),
        ('поступила', 'поступила на склад')
    )
    supply = models.ForeignKey(
        'Supply',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='номер поставки'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='кол-во',
        null=False
    )
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
    purchase_price = models.DecimalField(
        null=False,
        max_digits=7,
        decimal_places=2,
        verbose_name='цена закупа'
    )
    total_purchase_price = models.DecimalField(
        null=False,
        max_digits=15,
        decimal_places=2,
        verbose_name='сумма поставки'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_list,
        null=False,
        verbose_name='статус',
        default='заказана'
    )
    order = models.ForeignKey(
        'Order',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='номер заказа'
    )

    def is_actual(self):
        """Возвращает True если позиция поставки
        актуальная и False - если нет"""
        return True if self.status == 'заказана' else False

    class Meta:
        verbose_name = 'Позицию поставки'
        verbose_name_plural = 'Позиции поставок'

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_purchase_price(good, supplier):
        """
        возвращает из БД закупочную цену товара
        :param good: экземпляр класса Good
        :param supplier: экземпляр класса Supplier
        :return: закупочную цену товара(типа - Decimal)
        """
        purchase_prices = good.purchaseprice_set.all()
        pp_object = purchase_prices.get(supplier=supplier.id)
        purchase_price = pp_object.purchase_price
        return purchase_price

    def get_order_id(self):
        """возвращает номер заказа"""
        return self.order_id if self.order_id else ''


class Good(models.Model):
    """представляет товар"""
    UNITS = (
        ('кг', 'килограммы'),
        ('шт', 'штуки')
    )
    title = models.CharField(
        max_length=100,
        verbose_name='название'
    )
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
    storage_quantity = models.PositiveIntegerField(
        verbose_name='свободное кол-во на складе',
        null=True
    )
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
        verbose_name='продается'
    )
    artikul = models.CharField(
        max_length=100,
        verbose_name='артикул'
    )
    suppliers = models.ManyToManyField(
        Supplier,
        verbose_name='поставщики'
    )
    photo = models.ImageField(
        null=True,
        verbose_name='фото'
    )

    class Meta:
        verbose_name = 'Товары'
        verbose_name_plural = 'Товары'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_reserve_quantity(self):
        """возвращает кол-во данного товара, находящегося в резерве"""
        reserves = self.reserve_set.all()
        reserve_quantity = self.reserve_set.filter(is_actual=True).aggregate(
            Sum('quantity'))['quantity__sum']
        return 0 if not reserve_quantity else reserve_quantity

    def get_total_quantity(self):
        """возвращает общее кол-во данного товара
        на склада(свободный остаток+резерв)"""
        reserves = self.reserve_set.all()
        reserve_quantity = reserves.filter(is_actual=True).aggregate(
            Sum('quantity'))['quantity__sum']
        return self.storage_quantity if not reserve_quantity else\
            reserve_quantity + self.storage_quantity


class PurchasePrice(models.Model):
    """представляет закупочную цену товара"""
    purchase_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='цена закупа'
    )
    supplier = models.ForeignKey(
        'Supplier',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='поставщик'
    )
    good = models.ForeignKey(
        'Good',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='товар'
    )

    def __str__(self):
        return f'{self.supplier}, {self.purchase_price}'

    class Meta:
        verbose_name = 'Закупочную цену'
        verbose_name_plural = 'Закупочные цены'


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
        verbose_name='статус',
        default='создан'
    )
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.PROTECT,
        verbose_name='покупатель'
    )
    positions = models.PositiveIntegerField(
        null=False,
        verbose_name='кол-во позиций'
    )
    total_coast = models.DecimalField(
        null=False,
        max_digits=15,
        decimal_places=2,
        verbose_name='Сумма заказа'
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        null=False,
        verbose_name='время создания'
    )
    qr_code = models.TextField(
        max_length=1000,
        null=True,
        verbose_name='QR-код'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Клиентские заказы'

    def __str__(self):
        return f'{self.id}'


class OrderItems(models.Model):
    """представляет список всех позиций в заказе"""
    order = models.ForeignKey(
        'Order',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='заказ'
    )
    good = models.ForeignKey(
        'Good',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='товар'
    )
    position_price = models.DecimalField(
        null=False,
        max_digits=15,
        decimal_places=2,
        verbose_name='Сумма по позиции'
    )
    position_quantity = models.PositiveIntegerField(
        null=False,
        verbose_name='кол-во товара в позиции'
    )

    def __str__(self):
        return str(self.id)

    def get_reserves(self):
        """подгружает кол-во резервов по позиции"""
        try:
            reserves = Reserve.objects.filter(
                order_item_id=self.id).filter(is_actual=True)
        except Reserve.DoesNotExist:
            reserve_quantity = 0
        else:
            reserve_quantity = reserves.aggregate(Sum('quantity'))['quantity__sum']
            reserve_quantity = reserve_quantity if reserve_quantity else 0
        return reserve_quantity


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Детализация заказов'


class Reserve(models.Model):
    """представляет резерв товара под заказ"""
    order = models.ForeignKey(
        'Order',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='заказ'
    )
    good = models.ForeignKey(
        'Good',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='товар'
    )
    quantity = models.PositiveIntegerField(
        null=False,
        verbose_name='резерв'
    )
    is_actual = models.BooleanField(
        null=False,
        verbose_name='актуальность',
        default=True
    )
    time_create = models.DateTimeField(
        auto_now_add=True,
        null=False,
        verbose_name='время создания'
    )

    order_item = models.ForeignKey(
        'OrderItems',
        null=False,
        on_delete=models.PROTECT,
        verbose_name='Позиция в заказе'
    )

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name = 'Резерв'
        verbose_name_plural = 'Резерв'




















