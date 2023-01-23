from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse('Главная страница yatube')


def group_posts(request, text):
    return HttpResponse(f'Посты вот с этой строкой {text}')
