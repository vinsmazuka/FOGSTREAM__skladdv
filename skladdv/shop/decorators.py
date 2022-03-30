from django.shortcuts import HttpResponse


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


def user_is_staff(func_to_deco):
    """
    проверяет, что пользователь относится к категории staff
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request, *args, **kwargs):
        """функция-обертка"""
        if request.user.is_staff:
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Доступ к данной странице есть только у сотрудников склада,\n'
                                'для получения доступа обратитесь к администратору')
    return wrapper


def user_is_not_staff(func_to_deco):
    """
    проверяет, что пользователь не относится к категории staff
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request, *args, **kwargs):
        """функция-обертка"""
        if not request.user.is_staff:
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Доступ к данной странице есть только у покупателей')
    return wrapper




