
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'styles'

urlpatterns = [
    path('', views.StylesList, name='styles'),
    path('main2', views.main2),
    path('detail/', views.StyleDetail, name='detail'),
    path('details/<star_name>', views.StarView.as_view()),

    path('details/', views.redirect, name='details'),

    path('test', views.test),
]
