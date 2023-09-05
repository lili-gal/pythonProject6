from django.db import models
from config.settings import AUTH_USER_MODEL

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    fio = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.CharField(max_length=100, verbose_name='email')
    comment = models.TextField(max_length=1000, **NULLABLE, verbose_name='Комментарий')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')
    def __str__(self):
        return f'{self.fio} {self.email}'


class Mailing(models.Model):
    clients = models.ManyToManyField(Client)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')
    time = models.TimeField(verbose_name='Время рассылки')

    class Interval(models.TextChoices):
        DAY = 'Раз в день',
        WEEK = 'Раз в неделю',
        MONTH = 'Раз в месяц'

    interval = models.CharField(max_length=15, choices=Interval.choices, default=Interval.DAY, verbose_name='Периодичность')

    class Status(models.TextChoices):
        CREATED = 'Создана',
        RUNNING = 'Запущена',
        FINISHED = 'Завершена'

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED, verbose_name='Статус рассылки')

    def __str__(self):
        return f'{self.time} {self.interval} {self.status}'


class Message(models.Model):
    message_object = models.CharField(max_length=100, **NULLABLE, verbose_name='Тема письма')
    message_body = models.TextField(max_length=2000, verbose_name='Тело письма')
    mailing = models.OneToOneField(Mailing, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.message_object} {self.message_body}'


class MailingLog(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    mailing_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Время последней попытки')

    class Status(models.TextChoices):
        SUCCESS = 'Успешно',
        FAILED = 'Неудача'

    status = models.CharField(max_length=7, choices=Status.choices, verbose_name='Статус отправки')
    response = models.TextField(**NULLABLE, verbose_name='Ответ почтового сервера')

    def __str__(self):
        return f'{self.mailing_datetime} {self.status}'


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Текст')
    image = models.ImageField(upload_to='uploads/', verbose_name='Изображение', **NULLABLE)
    public_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    watch = models.IntegerField(verbose_name='Количество просмотров', default=0)
