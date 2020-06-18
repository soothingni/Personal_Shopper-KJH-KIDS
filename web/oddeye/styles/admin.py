from django.contrib import admin
from .models import Star, Star_embedding, Star_embedding2, Star_embedding3

# Register your models here.
class StarAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'likey', 'tag', 'style')

class StarEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('no', 'star_embedding')

class StarEmbeddingAdmin1(admin.ModelAdmin):
    list_display = ('no', 'star_embedding')

class StarEmbeddingAdmin2(admin.ModelAdmin):
    list_display = ('no', 'star_embedding')



admin.site.register(Star, StarAdmin)
admin.site.register(Star_embedding, StarEmbeddingAdmin)
admin.site.register(Star_embedding3, StarEmbeddingAdmin1)
admin.site.register(Star_embedding2, StarEmbeddingAdmin2)