from django.db import models
from django.conf import settings

# Create your models here.
class Star(models.Model):
    no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    likey = models.IntegerField()
    tag = models.CharField(max_length=30)
    style = models.IntegerField()
    category = models.CharField(max_length=100, blank=True, null=True)
#    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='likes')
    # @property
    # def like_count(self):
    #     return self.likes.count()


    
    # likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #                                        blank=True,
    #                                        related_name='like_style')

    def __str__(self):
        return self.name+'_'+str(self.style)

    class Meta:
        db_table = 'star'
        verbose_name = '스타'
        verbose_name_plural = '스타'


class Star_embedding3(models.Model):
    no = models.ForeignKey(Star, on_delete=models.CASCADE)
    star_embedding = models.CharField(max_length=2000)

    def __str__(self):
        return self.star_embedding

    class Meta:
        db_table = 'star_embedding3'
        verbose_name = '스타 임베딩3'
        verbose_name_plural = '스타 임베딩3'

class Star_embedding(models.Model):
    no = models.IntegerField()
    star_embedding = models.CharField(max_length=2000)

    def __str__(self):
        return self.star_embedding

    class Meta:
        db_table = 'star_embedding'
        verbose_name = '스타 임베딩1'
        verbose_name_plural = '스타 임베딩1'

class Star_embedding2(models.Model):
    no = models.IntegerField()
    star_embedding = models.CharField(max_length=2000)

    def __str__(self):
        return self.star_embedding

    class Meta:
        db_table = 'star_embedding2'
        verbose_name = '스타 임베딩2'
        verbose_name_plural = '스타 임베딩2'