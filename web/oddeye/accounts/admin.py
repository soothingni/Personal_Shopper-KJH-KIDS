from django.contrib import admin
from .models import OddeyeUsers

# Register your models here.
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('no', 'username', 'password', 'following', 'wish_list', 'register_date')
#
admin.site.register(OddeyeUsers, AccountsAdmin)