from django.contrib import admin
from .models import Products, ProductsEmbedding3, ProductsEmbedding, ProductsEmbedding2

# Register your models here.
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'product_name', 'price_original', 'price_discount', 'super_category', 'base_category', 'sub_category', 'img_url', 'product_url')

class ProductsEmbeddingAdmin3(admin.ModelAdmin):
    list_display = ('product_ID', 'product_embedding')

class ProductsEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('product_ID', 'product_embedding')

class ProductsEmbeddingAdmin2(admin.ModelAdmin):
    list_display = ('product_ID', 'product_embedding')


admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsEmbedding3, ProductsEmbeddingAdmin3)
admin.site.register(ProductsEmbedding, ProductsEmbeddingAdmin)
admin.site.register(ProductsEmbedding2, ProductsEmbeddingAdmin2)
