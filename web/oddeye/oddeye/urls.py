from django.contrib import admin
from django.urls import path, include
import styles.views
import accounts.views
import products.views

urlpatterns = [
    path('', styles.views.main, name='main'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('styles/', include('styles.urls')),
    path('products/', include('products.urls')),
    path('aboutus/', accounts.views.aboutus, name='aboutus'),
]
