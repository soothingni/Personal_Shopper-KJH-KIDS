
from django.contrib import admin
from django.urls import path
from . import views
import products.views

app_name = 'styles'

urlpatterns = [
    path('<cat_no>', views.StylesList, name='list'),
    path('', views.redirectlist, name='styles'),
    path('details/<star_name>/', views.StarView.as_view(), name='detail_styles'),
    path('details/<star_name>/<int:pk>', views.StarView.as_view()),
]
