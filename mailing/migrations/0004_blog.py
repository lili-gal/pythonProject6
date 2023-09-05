# Generated by Django 4.2.3 on 2023-09-05 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0003_alter_client_user_alter_mailing_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('body', models.TextField(verbose_name='Текст')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Изображение')),
                ('public_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('watch', models.IntegerField(verbose_name='Количество просмотров')),
            ],
        ),
    ]