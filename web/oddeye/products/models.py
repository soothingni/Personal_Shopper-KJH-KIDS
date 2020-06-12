from django.db import models

# Create your models here.
class Products(models.Model):
    product_ID = models.IntegerField(primary_key=True, verbose_name="상품 ID")
    super_category = models.CharField(max_length=20, verbose_name="대분류")
    base_category = models.CharField(max_length=20, verbose_name="중분류")
    sub_category = models.CharField(max_length=20, verbose_name="소분류")
    img_url = models.CharField(max_length=300, verbose_name="이미지 URL")
    product_url = models.CharField(max_length=300, verbose_name="상품 URL")

    def __str__(self):
        return self.product_ID

    class Meta:
        db_table = "products"
        verbose_name = "상품"
        verbose_name_plural = "상품"

class ProductsEmbedding(models.Model):
    product_ID = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_embedding = models.CharField(max_length=1000)

    def __str__(self):
        return self.product_ID

    class Meta:
        db_table = "products_embedding"
        verbose_name = "상품 임베딩"
        verbose_name_plural = "상품 임베딩"