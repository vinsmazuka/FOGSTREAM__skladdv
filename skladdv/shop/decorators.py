from django.shortcuts import HttpResponse


def user_is_authenticated(func_to_deco):
    """проверяет, залогинен ли пользователь"""
    def wrapper(request):
        if request.user.is_authenticated:
            print('да')
            return func_to_deco(request)
        else:
            return HttpResponse('Залогиньтесь, чтобы получить доступ к странице')
    return wrapper

