
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.jsontest, name='products'),
    # path('jsontest',views.jsontest)
]