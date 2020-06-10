from django.db import models

# Create your models here.
class User(models.Model):
    no = models.CharField(primary_key=True, max_length=15, verbose_name="NO")
    id = models.CharField(max_length=15, verbose_name="아이디")
    password = models.CharField(max_length=15, verbose_name="패스워드")
    following = models.CharField(max_length=1000, verbose_name="팔로잉")
    wish_list = models.CharField(max_length=1000, verbose_name="위시리스트")
    register_date = models.DateTimeField(auto_now_add=True, verbose_name="등록날짜")

    def __str__(self):
        return self.id

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "user"