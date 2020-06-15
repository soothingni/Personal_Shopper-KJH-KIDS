
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'styles'

urlpatterns = [
    path('', views.StylesList, name='styles'),
    path('details/<star_name>', views.StarView.as_view(), name='detail_styles'),
]
