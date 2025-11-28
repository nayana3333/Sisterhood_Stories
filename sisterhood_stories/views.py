from django.shortcuts import render
from django.utils import timezone
from stories.models import Post, Story, Like
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    # Get all posts ordered by creation date (newest first)
    posts = Post.objects.select_related('author').prefetch_related('like_set', 'comment_set').order_by('-created_at')[:20]
    
    # Get active stories
    active_stories = []
    if request.user.is_authenticated:
        active_stories = Story.objects.filter(
            expiry__gt=timezone.now()
        ).select_related('user').order_by('-created_at')[:8]
    
    # Get liked post IDs for current user
    liked_post_ids = []
    if request.user.is_authenticated and posts:
        post_ids = [p.id for p in posts]
        liked_post_ids = list(Like.objects.filter(
            user=request.user,
            post_id__in=post_ids
        ).values_list('post_id', flat=True))
    
    return render(request, 'home.html', {
        'posts': posts,
        'active_stories': active_stories,
        'liked_post_ids': liked_post_ids
    })
