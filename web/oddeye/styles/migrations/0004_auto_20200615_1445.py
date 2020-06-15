# Generated by Django 3.0.6 on 2020-06-15 05:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('styles', '0003_auto_20200612_2004'),
    ]

    operations = [
        migrations.AddField(
            model_name='star',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='star_embedding',
            name='star_embedding',
            field=models.CharField(max_length=2000),
        ),
    ]