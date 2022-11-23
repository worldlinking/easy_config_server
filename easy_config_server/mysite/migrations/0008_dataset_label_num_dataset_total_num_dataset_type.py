# Generated by Django 4.1.2 on 2022-11-15 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mysite", "0007_remove_dataset_type_alter_dataset_format_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="label_num",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dataset",
            name="total_num",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dataset",
            name="type",
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
