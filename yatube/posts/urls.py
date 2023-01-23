from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('group/<str:text>/', views.group_posts)
]
