
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.productview, name='products'),
    path('<int:pk>', views.prod_list.as_view(), name='prod_list'),
    path('clientinput',views.ClientInput.as_view(), name='clientinput'),
    path('prod2prod', views.modal_star_and_prod),
]