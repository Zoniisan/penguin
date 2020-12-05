# Generated by Django 3.1.3 on 2020-11-25 14:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20201125_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=20, verbose_name='タイトル')),
                ('body', models.CharField(max_length=20, verbose_name='本文')),
                ('start_datetime', models.DateTimeField(blank=True, null=True, verbose_name='開始日時')),
                ('finish_datetime', models.DateTimeField(blank=True, null=True, verbose_name='終了日時')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_datetime', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='担当')),
            ],
            options={
                'verbose_name': 'お知らせ',
                'verbose_name_plural': 'お知らせ',
            },
        ),
    ]
