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
    проверяет, относится ли пользователь к категории staff
    :param func_to_deco: функция, которую необходимо обернуть
    :return: функцию-обертку wrapper
    """
    def wrapper(request):
        """функция-обертка"""
        if request.user.is_staff:
            return func_to_deco(request)
        else:
            return HttpResponse('Доступ к данной странице есть только у сотрудников склада,\n'
                                'для получения доступа обратитесь к администратору')
    return wrapper


