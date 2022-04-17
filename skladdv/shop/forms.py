from django.core.validators import RegexValidator
from django.forms import CharField, ChoiceField, Form, ModelForm, IntegerField, EmailField, DecimalField

from .models import Supplier, Good


class CartAddGood(Form):
    """
    форма для добавления товара в корзину покупателя
    """
    quantity = IntegerField(min_value=1)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')


class OrderChangeStatus(Form):
    """
    форма для изменения статуса заказа
    """
    CHOICES = (
        ('создан', 'создан'),
        ('заказан', 'заказан'),
        ('собран', 'собран'),
        ('исполнен', 'исполнен'),
        ('отменен', 'отменен')
    )
    status = ChoiceField(choices=CHOICES)


class StaffCartAddGood(Form):
    """
    форма для добавления товара в корзину персонала
    """
    quantity = IntegerField(min_value=1)
    quantity.widget.attrs.update(size='15')
    quantity.widget.attrs.update(placeholder='кол-во(целое число)')
    supplier = ChoiceField()
    order = IntegerField(min_value=1, required=False)
    order.widget.attrs.update(size='15')
    order.widget.attrs.update(placeholder='№ заказа')

    def __init__(self, *args, **kwargs):
        super(StaffCartAddGood, self).__init__(*args, **kwargs)
        self.fields['supplier'].choices = list((supplier.id, supplier.name) for
                                               supplier in Supplier.objects.filter(is_actual=True))


class SupplierCreate(Form):
    """
    форма для создания нового поставщика
    """
    ph_numb_validator = RegexValidator(regex=r"^7\d{10}$",
                                       message='Значение в поле "Телефон" не соответствует маске')
    inn_validator = RegexValidator(regex=r"^\d{10}$",
                                   message='Значение в поле "ИНН" не соответствует маске')
    ogrn_validator = RegexValidator(regex=r"^\d{13}$",
                                    message='Значение в поле "ОГРН" не соответствует маске')

    name = CharField(max_length=30, label="Имя")
    name.widget.attrs.update(placeholder='ООО "Росинка"', size='70')

    inn = CharField(max_length=10, min_length=10,
                    label="ИНН", validators=[inn_validator])
    inn.widget.attrs.update(placeholder='4401116480', size='70')

    ogrn = CharField(max_length=13, min_length=13,
                     label="ОГРН", validators=[ogrn_validator])
    ogrn.widget.attrs.update(placeholder='1144400000425', size='70')

    address = CharField(max_length=70, label="Адрес")
    address.widget.attrs.update(
        placeholder='г. Хабаровск, ул Промышленная, д.6 оф 3',
        size='70'
    )

    contact_person = CharField(max_length=70, label="Контактное лицо")
    contact_person.widget.attrs.update(
        placeholder='Иванов Василий Петрович',
        size='70'
    )

    telephone = CharField(max_length=11, min_length=11,
                          label="Телефон", validators=[ph_numb_validator])
    telephone.widget.attrs.update(placeholder='79244067819', size='70')

    email = EmailField(max_length=30, label="Email", )
    email.widget.attrs.update(placeholder='djcatswill@mail.ru', size='70')

    good = ChoiceField(label="Товар")

    purchase_price = DecimalField(
        min_value=1,
        max_digits=7,
        decimal_places=2,
        required=False,
        label="Закупочная цена"
    )
    purchase_price.widget.attrs.update(placeholder='пример: 45,56')

    def __init__(self, *args, **kwargs):
        super(SupplierCreate, self).__init__(*args, **kwargs)
        self.fields['good'].choices = list((good.id, good.title) for
                                           good in Good.objects.filter(available_for_order=True))
        self.fields['good'].choices.append((0, ""))





