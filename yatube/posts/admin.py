from django.contrib import admin

from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """Custom admin model for posts."""
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Custom admin model for groups"""
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    """Custom admin model for comments."""
    list_display = (
        'post',
        'author',
        'text',
        'pub_date'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)


class FollowAdmin(admin.ModelAdmin):
    """Custom admin model for follow."""
    list_display = (
        'user',
        'author'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
