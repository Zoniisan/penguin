# Generated by Django 3.1.4 on 2020-12-08 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voteschedule',
            name='theme_list',
            field=models.ManyToManyField(to='theme.Theme', verbose_name='統一テーマ案'),
        ),
    ]
