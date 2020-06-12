from django.contrib import admin
from .models import Star, Star_embedding

# Register your models here.
class StarAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'likey', 'tag', 'style')

class StarEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('no', 'star_embedding')

admin.site.register(Star, StarAdmin)
admin.site.register(Star_embedding, StarEmbeddingAdmin)