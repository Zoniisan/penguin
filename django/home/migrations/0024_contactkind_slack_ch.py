# Generated by Django 3.1.4 on 2020-12-04 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_identifytoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactkind',
            name='slack_ch',
            field=models.CharField(default='dummy', help_text='#は除いて登録してください', max_length=50, verbose_name='slack'),
            preserve_default=False,
        ),
    ]