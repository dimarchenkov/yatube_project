from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """Определение полей, которые должны отображаться в админке."""
    list_display: tuple = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
