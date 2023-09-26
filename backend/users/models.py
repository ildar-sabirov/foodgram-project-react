from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

USERNAME_LENGTH = 150
EMAIL_LENGTH = 254
FIRST_NAME_LENGTH = 150
LAST_NAME_LENGTH = 150


class User(AbstractUser):
    """
    Модель пользователя платформы.
    """
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Email',
    )
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя',
        validators=[validate_username],
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_LENGTH,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        blank=False,
        verbose_name='Фамилия',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
