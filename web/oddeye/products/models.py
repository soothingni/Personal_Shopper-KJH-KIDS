from django.db import models

# Create your models here.
class Products(models.Model):
    product_ID = models.IntegerField(primary_key=True, verbose_name="상품 ID")
    product_name = models.CharField(max_length=300, verbose_name="상품명", blank=True, null=True)
    price_original = models.IntegerField(verbose_name="상품 가격(정가)", blank=True, null=True)
    price_discount = models.IntegerField(verbose_name="상품 할인가격", blank=True, null=True)
    super_category = models.IntegerField(verbose_name="대분류", blank=True, null=True)
    base_category = models.IntegerField(verbose_name="중분류", blank=True, null=True)
    sub_category = models.IntegerField(verbose_name="소분류", blank=True, null=True)
    img_url = models.CharField(max_length=500, verbose_name="이미지 URL", blank=True, null=True)
    product_url = models.CharField(max_length=500, verbose_name="상품 URL", blank=True, null=True)

    def __str__(self):
        return str(self.product_ID)

    class Meta:
        db_table = "products"
        verbose_name = "상품"
        verbose_name_plural = "상품"


class ProductsEmbedding3(models.Model):
    product_ID = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name="상품 ID")
    product_embedding = models.CharField(max_length=2000, verbose_name="상품 임베딩값")

    def __str__(self):
        return str(self.product_ID)

    class Meta:
        db_table = "products_embedding3"
        verbose_name = "상품 임베딩3"
        verbose_name_plural = "상품 임베딩3"

class ProductsEmbedding(models.Model):
    product_ID = models.IntegerField()
    product_embedding = models.CharField(max_length=2000, verbose_name="상품 임베딩값")

    def __str__(self):
        return self.product_ID

    class Meta:
        db_table = "products_embedding"
        verbose_name = "상품 임베딩"
        verbose_name_plural = "상품 임베딩"

class ProductsEmbedding2(models.Model):
    product_ID = models.IntegerField()
    product_embedding = models.CharField(max_length=2000, verbose_name="상품 임베딩값")

    def __str__(self):
        return self.product_ID

    class Meta:
        db_table = "products_embedding2"
        verbose_name = "상품 임베딩2"
        verbose_name_plural = "상품 임베딩2"