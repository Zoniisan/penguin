# Generated by Django 3.1.3 on 2020-12-02 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_auto_20201202_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact', to='home.contactkind', verbose_name='お問い合わせ種別'),
        ),
    ]