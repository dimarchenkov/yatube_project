from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    template = 'posts/index.html'
    return render(request, template)


def group_posts(request):
    template = 'posts/group_list.html'
    return render(request, template)
