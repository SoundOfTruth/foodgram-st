from django.db import models
from django.contrib.auth.models import AbstractUser

from constants import MAX_FIRSTNAME_LENGTH, MAX_LASTNAME_LENGTH, MAX_EMAIL_LENGTH


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_FIRSTNAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LASTNAME_LENGTH,
    )
    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name='Фото',
        upload_to='users/images/',
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписка',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user_id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='subscription_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user}: {self.author}'
