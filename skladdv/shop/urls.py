from django.urls import path

from . import views

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:good_id>/', views.detail, name='detail'),
    path('', views.index, name='index')
]
