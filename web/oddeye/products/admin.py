from django.contrib import admin
from .models import Products, ProductsEmbedding

# Register your models here.
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'super_category', 'base_category', 'sub_category', 'img_url', 'product_url')

class ProductsEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'product_embedding')

admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsEmbedding, ProductsEmbeddingAdmin)
