from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel


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


class Post(CreatedModel):
    """Post class."""
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
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
        help_text='Укажите название вашей группы',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        """Get post text."""
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'

    def __str__(self):
        return self.text[:15]


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'], name='unique_follow')
        ]
