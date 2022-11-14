# Generated by Django 4.1.2 on 2022-11-11 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tasks",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("userId", models.CharField(max_length=32, verbose_name="用户id")),
                ("taskName", models.CharField(max_length=32, verbose_name="任务名称")),
                (
                    "siteName",
                    models.CharField(
                        choices=[("微博", "微博"), ("twitter", "twitter")],
                        max_length=32,
                        verbose_name="目标网站名称",
                    ),
                ),
                ("keyword", models.CharField(max_length=32, verbose_name="检索关键词")),
                ("status", models.CharField(max_length=10, verbose_name="爬虫状态")),
                ("startTime", models.CharField(max_length=32, verbose_name="开始时间")),
                ("runtime", models.CharField(max_length=32, verbose_name="运行时间")),
                ("endTime", models.CharField(max_length=32, verbose_name="结束时间")),
                (
                    "jobid",
                    models.CharField(default="", max_length=32, verbose_name="爬虫任务id"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="wyNews",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="新闻名称")),
                ("content", models.CharField(max_length=255, verbose_name="新闻内容")),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="spider.tasks"
                    ),
                ),
            ],
            options={
                "db_table": "wyNews",
            },
        ),
        migrations.CreateModel(
            name="weibo",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=20,
                        primary_key=True,
                        serialize=False,
                        verbose_name="id",
                    ),
                ),
                ("screen_name", models.CharField(max_length=30, verbose_name="用户昵称")),
                ("text", models.CharField(max_length=2000, verbose_name="微博正文")),
                ("topics", models.CharField(max_length=200, verbose_name="话题")),
                ("location", models.CharField(max_length=100, verbose_name="发布位置")),
                ("created_at", models.DateTimeField(verbose_name="发布时间")),
                ("attitudes_count", models.IntegerField(default=0, verbose_name="点赞量")),
                ("comments_count", models.IntegerField(default=0, verbose_name="评论量")),
                ("reposts_count", models.IntegerField(default=0, verbose_name="转发量")),
                ("bid", models.CharField(max_length=12, verbose_name="bid")),
                ("user_id", models.CharField(max_length=20, verbose_name="用户id")),
                ("article_url", models.CharField(max_length=100, verbose_name="文章URL")),
                ("at_users", models.CharField(max_length=1000, verbose_name="艾特用户")),
                ("pics", models.CharField(max_length=3000, verbose_name="图片URL")),
                ("video_url", models.CharField(max_length=1000, verbose_name="视频URL")),
                ("source", models.CharField(max_length=30, verbose_name="发布工具")),
                (
                    "retweet_id",
                    models.CharField(max_length=20, verbose_name="retweet_id"),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="spider.tasks"
                    ),
                ),
            ],
            options={
                "db_table": "weibo",
            },
        ),
    ]
