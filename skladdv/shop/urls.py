from django.urls import path

from . import views

urlpatterns = [
    path('catalog/', views.index, name='index'),
    path('catalog/<int:good_id>', views.detail, name='detail')
]
