# Generated by Django 3.1.3 on 2020-12-02 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_auto_20201202_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='finished',
            field=models.BooleanField(default=False, verbose_name='対応完了'),
        ),
    ]
