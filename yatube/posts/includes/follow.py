from django.contrib.auth.decorators import login_required

from posts.models import Follow


@login_required
def follow(request, author):
    return Follow.objects.filter(author=author, user=request.user).exists()
