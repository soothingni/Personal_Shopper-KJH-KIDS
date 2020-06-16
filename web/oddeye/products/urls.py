
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.productview, name='products'),
    path('sembed/<int:pk>', views.star_embedding),
    path('pembed/<int:pk>',views.prod_embedding),
    path('<int:pk>', views.prod_list.as_view(), name='prod_list'),
    path('clientinput',views.ClientInput),
]