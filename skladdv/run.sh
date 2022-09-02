#!/bin/bash

echo "Начинаю миграции"
python manage.py makemigrations
python manage.py migrate
echo "Миграции завершены"

echo "Создаю суперпользователя"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell

echo "Запускаю сервер"
python manage.py runserver 0.0.0.0:80


