
from django.contrib import admin
from django.urls import path, include
from . import views
import accounts.views

urlpatterns = [
    path('login/',views.LoginView.as_view(), name='login'),
    path('register/',views.RegisterView.as_view(), name='register'),
    path('logout/', accounts.views.logout, name='logout'),
    path('myaccounts/', accounts.views.myaccounts, name='myaccounts'),

]
