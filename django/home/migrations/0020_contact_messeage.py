# Generated by Django 3.1.3 on 2020-12-02 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_auto_20201202_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='messeage',
            field=models.ManyToManyField(to='home.Message', verbose_name='返信メッセージ'),
        ),
    ]