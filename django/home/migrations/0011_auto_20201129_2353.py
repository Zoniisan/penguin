# Generated by Django 3.1.3 on 2020-11-29 23:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_auto_20201129_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name_kana',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='ひらがなで入力してください', regex='^[ぁ-んー]+$')], verbose_name='名（かな）'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name_kana',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='ひらがなで入力してください', regex='^[ぁ-んー]+$')], verbose_name='姓（かな）'),
        ),
    ]