
from django.contrib import admin
from django.urls import path, include
from . import views
import accounts.views

urlpatterns = [
    path('login/',views.LoginView.as_view(), name='login'),
    # path('login/',accounts.views.login,name='login'),
    path('register/',views.RegisterView.as_view(), name='register'),
    # path('accounts/', include('allauth.urls')),
    path('logout/', accounts.views.logout, name='logout'),
    # path('', views.main),
]
