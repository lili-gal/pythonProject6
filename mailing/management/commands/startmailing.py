import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from mailing.models import Mailing, Message, Client


logger = logging.getLogger(__name__)


def my_job(object, body, clients):
  send_mail(object, body, settings.EMAIL_HOST_USER, [*clients])


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
  help = "Runs APScheduler."

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    mails = Mailing.objects.all()
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
          args=[msg.message_object, msg.message_body, clients],
        )
      elif m.interval == 'Раз в неделю' and m.status == 'Запущена':
        scheduler.add_job(
          my_job,
          trigger=CronTrigger(day_of_week=0, hour=m.time.hour, minute=m.time.minute, second=m.time.second),
          id=f"my_job{m.id}",
          max_instances=1,
          replace_existing=True,
          args=[msg.message_object, msg.message_body, clients],
        )
      elif m.interval == 'Раз в месяц' and m.status == 'Запущена':
        scheduler.add_job(
          my_job,
          trigger=CronTrigger(day=1, hour=m.time.hour, minute=m.time.minute, second=m.time.second),
          id=f"my_job{m.id}",
          max_instances=1,
          replace_existing=True,
          args=[msg.message_object, msg.message_body, clients],
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
      logger.info("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      logger.info("Stopping scheduler...")
      scheduler.shutdown()
      logger.info("Scheduler shut down successfully!")