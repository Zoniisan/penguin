# Generated by Django 3.1.3 on 2020-11-29 11:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20201129_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='start_datetime',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='開始日時'),
        ),
    ]
