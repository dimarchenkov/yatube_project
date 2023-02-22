from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    """Main page."""

    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Posts page."""

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """User profile."""
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    posts_count = author.posts.count()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': author_posts,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post detail."""
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Create new post."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        temp_form = form.save(commit=False)
        temp_form.author = request.user
        temp_form.save()
        return redirect(
            'posts:profile', temp_form.author
        )
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    """Edit post."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    return render(
        request,
        template,
        {
            'form': form,
            'is_edit': True,
            'post': post,
        }
    )
