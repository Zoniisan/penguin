# Generated by Django 3.1.3 on 2020-11-30 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_auto_20201130_2120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
