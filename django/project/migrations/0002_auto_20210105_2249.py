# Generated by Django 3.1.4 on 2021-01-05 22:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kind',
            name='staff_list',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='担当スタッフ'),
        ),
    ]