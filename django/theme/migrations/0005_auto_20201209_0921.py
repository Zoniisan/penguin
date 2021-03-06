# Generated by Django 3.1.4 on 2020-12-09 09:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('theme', '0004_auto_20201209_0900'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='staff',
        ),
        migrations.AddField(
            model_name='theme',
            name='submit_staff',
            field=models.ForeignKey(blank=True, help_text='強制提出操作を行った場合、担当したスタッフが記録されます', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='theme_submit_staff', to=settings.AUTH_USER_MODEL, verbose_name='強制提出スタッフ'),
        ),
        migrations.AddField(
            model_name='theme',
            name='update_staff',
            field=models.ForeignKey(blank=True, help_text='編集操作を行った場合、担当したスタッフが記録されます', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='theme_update_staff', to=settings.AUTH_USER_MODEL, verbose_name='最終編集スタッフ'),
        ),
    ]
