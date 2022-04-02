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
        """функция-обертка
        :param group - группа, принадлежность к которой нужно проверить(тип - str)"""

        if request.user.groups.filter(name='Покупатели').exists():
            return func_to_deco(request, *args, **kwargs)
        else:
            return HttpResponse('Доступ к данной странице есть только у покупателей,\n'
                                'для получения доступа обратитесь к администратору')
    return wrapper






