# Generated by Django 3.0.6 on 2020-06-12 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_products_productsembedding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productsembedding',
            name='product_ID',
        ),
        migrations.DeleteModel(
            name='Products',
        ),
        migrations.DeleteModel(
            name='ProductsEmbedding',
        ),
    ]