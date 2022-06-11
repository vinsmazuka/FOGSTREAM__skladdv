from django.shortcuts import HttpResponse

from .models import Order


def user_is_authenticated(func_to_deco):
    """проверяет, залогинен ли пользователь
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Вам необходимо залогиниться')
    return wrapper


def staff_only(func_to_deco):
    """
    проверяет, принадлежность пользователя относится к группе "Персонал"
    Если пользователь не принадлежит к группе - закрывает доступ
    к страницам для персонала
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request, *args, **kwargs):
        """функция-обертка"""
        if request.user.groups.filter(name="Персонал").exists():
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Доступ к данной странице есть только у сотрудников склада,\n'
                                'для получения доступа обратитесь к администратору')
    return wrapper


def customer_only(func_to_deco):
    """
    проверяет, принадлежность пользователя относится к группе "Покупатели"
    Если пользователь не принадлежит к группе - закрывает доступ
    к страницам для покупателей
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request, *args, **kwargs):
        """функция-обертка"""
        if request.user.groups.filter(name='Покупатели').exists():
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Доступ к данной странице есть только у покупателей,\n'
                                'для получения доступа обратитесь к администратору')
    return wrapper


def check_created_by(func_to_deco):
    """
    Открывает доступ к странице пользователям из
    группы "Персонал" или покупателю, кот создал заказ,
    другим пользователям - блокирует доступ
    """
    def wrapper(request, *args, **kwargs):
        """функция-обертка"""
        order = Order.objects.get(pk=kwargs['order_id'])
        if request.user.groups.filter(name="Персонал").exists():
            return func_to_deco(request, *args, **kwargs)
        elif request.user.id == order.user_id:
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('У вас нет доступа к данной странице')
    return wrapper






