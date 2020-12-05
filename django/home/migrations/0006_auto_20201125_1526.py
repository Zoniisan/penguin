# Generated by Django 3.1.3 on 2020-11-25 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_notice_stop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='finish_datetime',
            field=models.DateTimeField(blank=True, help_text='空欄にした場合、永久的に公開されます', null=True, verbose_name='終了日時'),
        ),
        migrations.AlterField(
            model_name='notice',
            name='start_datetime',
            field=models.DateTimeField(blank=True, help_text='空欄にした場合、すぐに公開されます', null=True, verbose_name='開始日時'),
        ),
    ]
