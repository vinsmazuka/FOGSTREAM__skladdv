from mptt.models import MPTTModel, TreeForeignKey

from django.db import models


class Good(models.Model):
    """представляет товар"""
    UNITS = (
        ('кг', 'килограммы'),
        ('шт', 'штуки')
    )
    title = models.CharField(max_length=100, verbose_name='название')
    category = TreeForeignKey('Category',
                              on_delete=models.PROTECT,
                              related_name='goods',
                              null=False,
                              verbose_name='категория'
                              )
    price = models.IntegerField(verbose_name='цена')
    quantity = models.IntegerField(verbose_name='кол-во на складе', null=True)
    unit = models.CharField(max_length=2, choices=UNITS, null=False)
    time_create = models.DateTimeField(auto_now_add=True,
                                       verbose_name='время создания'
                                       )
    available_for_order = models.BooleanField(default=True,
                                              verbose_name='продается')
    artikul = models.CharField(max_length=100, verbose_name='артикул')

    def __str__(self):
        return self.title


class Category(MPTTModel):
    """представляет категорию товара"""
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey('self',
                            on_delete=models.PROTECT,
                            null=True,
                            blank=True,
                            related_name='children',
                            verbose_name='родительская категория'
                            )

    def __str__(self):
        return self.name
