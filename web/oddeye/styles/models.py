from django.db import models

# Create your models here.
class Star(models.Model):
    no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    likey = models.IntegerField()
    tag = models.CharField(max_length=30)
    style = models.IntegerField()

    def __str__(self):
        return self.name+'_'+str(self.style)

    class Meta:
        db_table = 'star'
        verbose_name = '스타'
        verbose_name_plural = '스타'


class Star_embedding(models.Model):
    no = models.ForeignKey(Star, on_delete=models.CASCADE)
    star_embedding = models.CharField(max_length=1000)

    def __str__(self):
        return self.star_embedding

    class Meta:
        db_table = 'star_embedding'
        verbose_name = '스타 임베딩'
        verbose_name_plural = '스타 임베딩'
