# Generated by Django 4.2.3 on 2023-09-05 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0004_blog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='watch',
            field=models.IntegerField(default=0, verbose_name='Количество просмотров'),
        ),
    ]
