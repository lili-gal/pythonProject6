from django.contrib import admin
from .models import Client, Mailing, MailingLog, Message, Blog


# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('fio', 'email', 'comment')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('time', 'interval', 'status')


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('mailing_datetime', 'status')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_object',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'watch', 'public_date')
