from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post
from posts.includes.follow import follow
from posts.includes.paginator import paginator

User = get_user_model()


# Главная страница
@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator(post_list, settings.PAGE_OBJ_COUNT, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница конкретного сообщества
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, settings.PAGE_OBJ_COUNT, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница автора
def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator(post_list, settings.PAGE_OBJ_COUNT, request)
    following = follow(request, author)
    context = {
        'following': following,
        'username': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница поста
def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comment_list = post.comments.all()
    page_obj = paginator(comment_list,
                         settings.PAGE_OBJ_COUNT,
                         request
                         )
    context = {
        'post': post,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница созадния поста
@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.id
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


# Страница редактирования поста
@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post,
                    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author_id = request.user.id
        comment.post_id = post_id
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = (Post.objects.filter(author__following__user=request.user))
    page_obj = paginator(post_list, settings.PAGE_OBJ_COUNT, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            author=author,
            user=request.user,
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username)
