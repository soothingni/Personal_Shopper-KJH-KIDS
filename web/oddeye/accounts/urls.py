
from django.contrib import admin
from django.urls import path, include
from . import views
import accounts.views

urlpatterns = [
    path('login/',accounts.views.login,name='login'),
    path('signup/',accounts.views.signup, name='signup'),
    # path('accounts/', include('allauth.urls')),
    path('logout/', accounts.views.logout, name='logout'),
    # path('', views.main),
]
