from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        verbose_name='электронная почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя', max_length=150, blank=True,
    )
    bio = models.TextField(verbose_name='о себе', blank=True)
    role = models.CharField(
        verbose_name='права доступа',
        choices=ROLES_CHOICES,
        default=USER,
        max_length=9,
    )

    def __str__(self) -> str:
        return self.username

    class Meta:

        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
