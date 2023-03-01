from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    """Group class."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True
    )
    description = models.TextField()

    class Meta:
        ordering = ['-title']

    def __str__(self):
        """Get Group name."""
        return self.title


class Post(models.Model):
    """Post class."""
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        """Get post text."""
        return self.text
