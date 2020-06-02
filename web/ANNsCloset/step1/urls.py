"""ANNsCloset URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
import step1.views
import login.views

app_name = 'step1'   #for namespace

urlpatterns = [
    path('', step1.views.main, name ='main'),
    path('stars/', step1.views.StarsView, name='stars'),
    path('goods/', step1.views.goods, name='goods'),
    # path('maintest/',step1.views.maintest, name='maintest')
#    path('list/', step1.views.ListView.as_view()),
#    path('detail/', step1.views.DetailView.as_view()),
]