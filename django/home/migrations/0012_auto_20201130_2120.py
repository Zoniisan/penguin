# Generated by Django 3.1.3 on 2020-11-30 21:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_auto_20201129_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='member',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='構成員'),
        ),
    ]
