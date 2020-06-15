from django.db import models

# Create your models here.
class OddeyeUsers(models.Model):
    no = models.AutoField(primary_key=True, verbose_name="NO")
    username = models.CharField(max_length=15, verbose_name="아이디")
    password = models.CharField(max_length=100, verbose_name="패스워드")
    following = models.CharField(max_length=1000, verbose_name="팔로잉")
    wish_list = models.CharField(max_length=1000, verbose_name="위시리스트")
    register_date = models.DateTimeField(auto_now_add=True, verbose_name="등록날짜")

    def __str__(self):
        return self.username

    class Meta:
        db_table = "oddeye_users"
        verbose_name = "oddeye_users"
        verbose_name_plural = "oddeye_users"