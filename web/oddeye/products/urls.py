
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.productview, name='products'),
    path('<pk>', views.prod_cat, name='cat')
]