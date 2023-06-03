import datetime
import logging
from fsite.models import Advertisment, Subscriber
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
logger = logging.getLogger(__name__)


def my_job():
    control_date = timezone.now() - datetime.timedelta(days=7)  # отматываем неделю назад
    all_subscribers = Subscriber.objects.all().values('user', 'user__username', 'user__email').distinct()
    for subscriber in all_subscribers:
        if (subscriber['user__email'] == ''):  # у пользователя нет Email, переходим к следующему
            continue
        advertisments = []  # формируем список объявлений за неделю
        advertisments_text = ''  # текстовая версия списка объявлений
        items = Advertisment.objects.filter(time_create__gt=control_date)
        if items.count() != 0:
            for item in items:
                item.url_for_letter = 'http://' + Site.objects.get_current().domain + ':8000/' + str(item.id) + '/'
                advertisments.append(item)
                advertisments_text += f'Объявление - {item.heading} / {item.body[:30]} : {item.url_for_letter} \n'
            html_content = render_to_string('letter_week.html', {'advertisments': advertisments})
            msg = EmailMultiAlternatives(
                subject=f'Объявления за неделю для {subscriber["user__username"]}',
                body=advertisments_text,
                from_email='s.gospodchikov@yandex.ru',
                to=[subscriber['user__email']],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    return


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # отправка писем раз в неделю
            id="my_job",
            max_instances=1,
            replace_existing=True,
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
