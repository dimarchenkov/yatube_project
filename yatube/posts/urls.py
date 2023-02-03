from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index),
    # path('group_list.html/', views.group_posts)
    path('group_list/', views.group_posts, name='posts_list')
]
