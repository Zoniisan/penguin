# Generated by Django 3.1.3 on 2020-11-25 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_notice'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notice',
            options={'ordering': ('start_datetime', 'create_datetime'), 'verbose_name': 'お知らせ', 'verbose_name_plural': 'お知らせ'},
        ),
        migrations.AddField(
            model_name='notice',
            name='stop',
            field=models.BooleanField(default=False, verbose_name='抑止'),
        ),
    ]