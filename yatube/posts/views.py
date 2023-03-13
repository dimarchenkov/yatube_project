from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import pages


@cache_page(20, key_prefix='index_page')
def index(request):
    """Main page."""
    post_list = Post.objects.all()
    page_obj = pages(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Posts page."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pages(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """User profile."""
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    page_obj = pages(author_posts, request)
    following = (
        request.user.is_authenticated
        and request.user.follower.filter(author=author).exists()
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Post detail."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
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
        return redirect('posts:profile', temp_form.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Edit post."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
        }
    )


@login_required
def add_comment(request, post_id):
    """Add comment"""
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """List follow posts."""
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pages(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Follow."""
    follow_author = get_object_or_404(User, username=username)
    if follow_author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=follow_author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Unfollow"""
    follow_author = get_object_or_404(User, username=username)
    request.user.follower.filter(author=follow_author).delete()
    return redirect('posts:profile', username)
