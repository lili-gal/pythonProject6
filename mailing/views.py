from smtplib import SMTPException

from apscheduler.jobstores.base import JobLookupError
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, UpdateView, DeleteView

from config.settings import CACHE_ENABLED
from users.models import User
from .models import Mailing, MailingLog, Client, Message, Blog
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from mailing.models import Mailing, Message, Client
from django_apscheduler.models import DjangoJobExecution
import logging

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def my_job(object, body, clients, id):
    try:
        send_mail(object, body, settings.EMAIL_HOST_USER, [*clients])
        MailingLog.objects.create(status='Успешно', mailing_id=id)
    except SMTPException as e:
        MailingLog.objects.create(status='Неудача', response=e, mailing_id=id)


def delete_old_job_executions(max_age=604_800):
  DjangoJobExecution.objects.delete_old_job_executions(max_age)


@login_required
def mailing(request):
    logger = logging.getLogger(__name__)
    mails = Mailing.objects.filter(user_id=request.user.pk)
    messages = Message.objects.all()
    for m in mails:
        msg = messages.get(mailing_id=m.id)
        clients = Client.objects.filter(mailing__id=m.id).values_list('email', flat=True)
        if m.interval == 'Раз в день' and m.status == 'Запущена':
            scheduler.add_job(
                my_job,
                trigger=CronTrigger(hour=m.time.hour, minute=m.time.minute, second=m.time.second),
                id=f"my_job{m.id}",
                max_instances=1,
                replace_existing=True,
                args=[msg.message_object, msg.message_body, clients, m.id],
            )
        elif m.interval == 'Раз в неделю' and m.status == 'Запущена':
            scheduler.add_job(
                my_job,
                trigger=CronTrigger(day_of_week=0, hour=m.time.hour, minute=m.time.minute, second=m.time.second),
                id=f"my_job{m.id}",
                max_instances=1,
                replace_existing=True,
                args=[msg.message_object, msg.message_body, clients, m.id],
            )
        elif m.interval == 'Раз в месяц' and m.status == 'Запущена':
            scheduler.add_job(
                my_job,
                trigger=CronTrigger(day=1, hour=m.time.hour, minute=m.time.minute, second=m.time.second),
                id=f"my_job{m.id}",
                max_instances=1,
                replace_existing=True,
                args=[msg.message_object, msg.message_body, clients, m.id],
            )

    logger.info("Added job 'my_job'.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info(
        "Added weekly job: 'delete_old_job_executions'."
    )

    try:
        if not scheduler.running:
            logger.info("Starting scheduler...")
            scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")
    if request.user.is_staff and request.user.groups.filter(name='manager').exists():
        if CACHE_ENABLED:
            key = f'mailing_info'
            mailing_info = cache.get(key)
            if mailing_info is None:
                mailing_info = Mailing.objects.order_by('id')
                cache.set(key, mailing_info)
            else:
                mailing_info = Mailing.objects.order_by('id')
    else:
        if CACHE_ENABLED:
            key = f'mailing_info'
            mailing_info = cache.get(key)
            if mailing_info is None:
                mailing_info = Mailing.objects.filter(user_id=request.user.pk).order_by('id')
                cache.set(key, mailing_info)
            else:
                mailing_info = Mailing.objects.filter(user_id=request.user.pk).order_by('id')
    is_manager = request.user.is_staff and request.user.groups.filter(name='manager').exists()
    active_count = len(mailing_info.filter(status='Запущена'))
    blog = Blog.objects.order_by('?')[:3]
    clients_count = len(Client.objects.all())
    return render(request, 'mailings.html', context={"mailing": mailing_info, "is_manager": is_manager, "blogs": blog, "mailing_count": len(mailing_info), "active_count": active_count, "client_count": clients_count})

@login_required
def mailing_logs(request):
    logs = []
    if request.user.is_staff and request.user.groups.filter(name='manager').exists():
        logs = MailingLog.objects.all()
    else:
        mailing = Mailing.objects.filter(user_id=request.user.pk)
        for m in mailing:
            logs = MailingLog.objects.filter(mailing_id=m.id)
    is_manager = request.user.is_staff and request.user.groups.filter(name='manager').exists()
    return render(request, 'mailing_logs.html', context={"mailing_log": logs, "is_manager": is_manager})

@login_required
def clients(request):
    if request.user.is_staff and request.user.groups.filter(name='manager').exists():
        clients_list = Client.objects.all()
    else:
        clients_list = Client.objects.filter(user_id=request.user.pk)
    is_manager = request.user.is_staff and request.user.groups.filter(name='manager').exists()
    return render(request, 'clients.html', context={"clients_list": clients_list, "is_manager": is_manager})


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ('clients', 'time', 'interval')
    success_url = reverse_lazy('mailing:mailings')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.pk
        self.object.save()
        msg = Message()
        msg.mailing_id = self.object.id
        msg.message_object = self.request.POST.get('object')
        msg.message_body = self.request.POST.get('message')
        msg.save()
        return super().form_valid(form)

@login_required
def mailing_info(request, mailing_id):
    is_manager = request.user.is_staff and request.user.groups.filter(name='manager').exists()
    mailing_info = Mailing.objects.get(id=mailing_id)
    msg = Message.objects.get(mailing_id=mailing_id)
    return render(request, 'mailing.html', context={"mailing": mailing_info, "msg": msg, "is_manager": is_manager})


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ('clients', 'time', 'interval')
    success_url = reverse_lazy('mailing:mailings')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        msg = Message.objects.get(mailing_id=self.kwargs['pk'])
        msg.message_object = self.request.POST.get('object')
        msg.message_body = self.request.POST.get('message')
        msg.save()
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing:mailings')

    def form_valid(self, form):
        try:
            scheduler.remove_job(f'my_job{self.kwargs["pk"]}')
        except JobLookupError:
            pass
        return super().form_valid(form)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ('fio', 'email', 'comment')
    success_url = reverse_lazy('mailing:clients')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.pk
        self.object.save()
        return super().form_valid(form)

@login_required
def client_info(request, client_id):
    client = Client.objects.all()
    client_info = client.get(id=client_id)
    is_manager = request.user.is_staff and request.user.groups.filter(name='manager').exists()
    return render(request, 'client.html', context={"client": client_info, "is_manager": is_manager})


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ('fio', 'email', 'comment')
    success_url = reverse_lazy('mailing:clients')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailing:clients')

@login_required
def toggle_activity(request, pk):
    mailing = Mailing.objects.get(id=pk)
    if mailing.status == 'Создана' or mailing.status == 'Завершена':
        scheduler.wakeup()
        mailing.status = 'Запущена'
        mailing.save()
    elif mailing.status == 'Запущена':
        scheduler.pause_job(f'my_job{pk}')
        mailing.status = 'Завершена'
        mailing.save()
    return redirect(reverse('mailing:mailings'))


@permission_required('users.change_user')
@login_required
def users(request):
    usrs = User.objects.all().order_by('id')
    if request.user.is_blocked:
        return render(request, 'is_blocked.html')
    return render(request, 'users.html', context={"usrs": usrs})


@permission_required('users.change_user')
@login_required
def ban(request, pk):
    user = User.objects.get(id=pk)
    if user.is_blocked:
        user.is_blocked = False
        user.save()
    elif not user.is_blocked:
        user.is_blocked = True
        user.save()
    return redirect(reverse('mailing:users'))


@cache_page(60)
def blog(request, pk):
    blog = Blog.objects.get(id=pk)
    blog.watch = blog.watch + 1
    blog.save()
    return render(request, 'blog.html', context={"blog": blog})
