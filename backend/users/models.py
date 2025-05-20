from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False
    )
    email = models.EmailField(
        verbose_name='Email',
        blank=False, null=False,
        unique=True
    )
    avatar = models.ImageField(
        verbose_name='Фото',
        upload_to='users/images/',
        default=None,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='subscriptions',
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='subscribers',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscription_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.author}'
