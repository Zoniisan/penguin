# Generated by Django 3.1.4 on 2020-12-09 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0005_auto_20201209_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='最終編集日時'),
        ),
    ]
