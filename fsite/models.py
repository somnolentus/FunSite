from django.db import models
from django.contrib.auth.models import User


TYPES = [('TANKS', 'Танки'),
         ('HILY', 'Хилы'),
         ('DD', 'ДД'),
         ('TRADES_PEOPLE', 'Торговцы'),
         ('GUILD_MATERS', 'Гилдмастеры'),
         ('QUEST_GILVERS', 'Квестгиверы'),
         ('BLACKMITHS', 'Кузнецы'),
         ('TANNERS', 'Кожевники'),
         ('POTION_MAKERS', 'Зельевары'),
         ('SPELL_MASTERS', 'Мастера заклинаний')]


class Category(models.Model):
    topic = models.CharField(max_length=15, choices=TYPES, unique=True, verbose_name='Категория')

    def __str__(self):
        return f'{self.topic}'


class Advertisment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'Пользователь')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    category = models.ForeignKey(Category, verbose_name=u'Категория', on_delete=models.DO_NOTHING)
    heading = models.CharField(max_length=255, verbose_name=u'Заголовок')
    body = models.TextField(verbose_name=u'Сожержимое')

    def __str__(self):
        return f'{self.user.username}: {self.heading[:30]} - {self.time_create}'


class Comment(models.Model):
    advertisment = models.ForeignKey(Advertisment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'Пользователь')
    comment = models.CharField(max_length=255, verbose_name=u'Отклик')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=u'Время создания')
    hidden = models.BooleanField(default=True, verbose_name=u'Вдимость')

    def hide(self, status):
        self.hidden = status
        self.save()


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def add_subscriber(user):
        Subscriber.objects.create(user=user)

    @staticmethod
    def delete_subscriber(user):
        Subscriber.objects.filter(user=user).delete()

    def __str__(self):
        user = self.user.username
        return f'{user}'


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', default=None, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, blank=True, null=True, default=None)
    date = models.DateField(blank=True, null=True)
