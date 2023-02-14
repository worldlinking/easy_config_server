from django.db import models
from mysite.models import User


# Create your models here.
class Tasks(models.Model):
    # 爬虫任务表
    # taskId = models.IntegerField(verbose_name='爬虫任务id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    taskName = models.CharField(verbose_name='任务名称', max_length=32, unique=True)
    siteName = models.CharField(verbose_name='目标网站名称', max_length=32)
    keyword = models.CharField(verbose_name='检索关键词', max_length=32)
    status = models.CharField(verbose_name='爬虫状态', max_length=10)
    startTime = models.CharField(verbose_name='开始时间', max_length=32)
    runtime = models.CharField(verbose_name='运行时间', max_length=32)
    endTime = models.CharField(verbose_name='结束时间', max_length=32)
    jobid = models.CharField(verbose_name='爬虫任务id', max_length=32, default='')
    dataNum = models.IntegerField(null=True, blank=True)  # 数据条目数量


# 每个网站建一个表
class wyNews(models.Model):
    task = models.ForeignKey(to='Tasks', to_field='id', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='新闻名称', max_length=255)
    content = models.CharField(verbose_name='新闻内容', max_length=255)

    class Meta:
        db_table = 'wyNews'


# class weibo(models.Model):
#     id = models.CharField(verbose_name='id', max_length=20, primary_key=True)
#     task = models.ForeignKey(to='Tasks', to_field='id', on_delete=models.CASCADE)
#     screen_name = models.CharField(verbose_name='用户昵称', max_length=30)
#     text = models.CharField(verbose_name='微博正文', max_length=2000)
#     topics = models.CharField(verbose_name='话题', max_length=200)
#     location = models.CharField(verbose_name='发布位置', max_length=100)
#     created_at = models.DateTimeField(verbose_name='发布时间')
#     attitudes_count = models.IntegerField(verbose_name='点赞量', default=0)
#     comments_count = models.IntegerField(verbose_name='评论量', default=0)
#     reposts_count = models.IntegerField(verbose_name='转发量', default=0)
#     bid = models.CharField(verbose_name='bid', max_length=12)
#     user_id = models.CharField(verbose_name='用户id', max_length=20)
#     article_url = models.CharField(verbose_name='文章URL', max_length=100)
#     at_users = models.CharField(verbose_name='艾特用户', max_length=1000)
#     pics = models.CharField(verbose_name='图片URL', max_length=3000)
#     video_url = models.CharField(verbose_name='视频URL', max_length=1000)
#     source = models.CharField(verbose_name='发布工具', max_length=30)
#     retweet_id = models.CharField(verbose_name='retweet_id', max_length=20)
#
#     class Meta:
#         db_table = 'weibo'

class weibo(models.Model):
    id = models.CharField(verbose_name='id', max_length=20, primary_key=True)
    task = models.ForeignKey(to='Tasks', to_field='id', on_delete=models.CASCADE)
    bid = models.CharField(verbose_name='bid', max_length=12)
    user_id = models.CharField(verbose_name='用户id', max_length=20)
    screen_name = models.CharField(verbose_name='用户昵称', max_length=30)
    text = models.CharField(verbose_name='微博正文', max_length=2000)
    longitude = models.FloatField(verbose_name='经度', null=True, blank=True)
    latitude = models.FloatField(verbose_name='纬度', null=True, blank=True)
    location = models.CharField(verbose_name='发布位置', max_length=100)
    created_at = models.DateTimeField(verbose_name='发布时间')
    attitudes_count = models.IntegerField(verbose_name='点赞量', default=0)
    comments_count = models.IntegerField(verbose_name='评论量', default=0)
    reposts_count = models.IntegerField(verbose_name='转发量', default=0)
    article_url = models.CharField(verbose_name='文章URL', max_length=100)
    pics = models.CharField(verbose_name='图片URL', max_length=3000)
    video_url = models.CharField(verbose_name='视频URL', max_length=1000)

    class Meta:
        db_table = 'weibo'


class weather(models.Model):
    id = models.CharField(verbose_name='id', max_length=20, primary_key=True)
    task = models.ForeignKey(to='Tasks', to_field='id', on_delete=models.CASCADE)
    rain1h = models.FloatField(null=True, blank=True)
    rain24h = models.FloatField(null=True, blank=True)
    rain12h = models.FloatField(null=True, blank=True)
    rain6h = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    windDirection = models.FloatField(null=True, blank=True)
    windSpeed = models.FloatField(null=True, blank=True)
    time = models.CharField(verbose_name='time', max_length=20)

    class Meta:
        db_table = 'weather'
