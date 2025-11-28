from django.views.generic import ListView, CreateView, View, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Post, Comment, Like, Story
from .forms import PostForm, StoryForm

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'stories/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Which posts current user liked (for filled-heart state)
        if self.request.user.is_authenticated:
            post_ids = [p.id for p in context['posts']]
            liked = Like.objects.filter(user=self.request.user, post_id__in=post_ids).values_list('post_id', flat=True)
            context['liked_post_ids'] = list(liked)
            
            # Get active stories (not expired and not viewed by current user)
            active_stories = Story.objects.filter(
                expiry__gt=timezone.now()
            ).exclude(
                views=self.request.user
            ).select_related('user').order_by('-created_at')
            
            context['active_stories'] = active_stories
        else:
            context['liked_post_ids'] = []
            context['active_stories'] = []
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'stories/post_form.html'
    fields = ['content', 'image', 'file', 'is_anonymous', 'pseudonym', 'allow_comments']
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        # ensure pseudonym only when anonymous
        if not form.cleaned_data.get('is_anonymous'):
            form.instance.pseudonym = ''
        else:
            # If anonymous but no pseudonym provided, keep it empty (will show as "Anonymous")
            pseudonym = form.cleaned_data.get('pseudonym', '').strip()
            form.instance.pseudonym = pseudonym
        
        messages.success(self.request, 'Your post has been created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class LikeToggleView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        # AJAX support
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'liked': created,  # if created, it's now liked
                'likes_count': post.like_set.count(),
                'post_id': post.id,
            })
        return redirect('stories:post_list')


@method_decorator(login_required, name='dispatch')
class PostDeleteView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if not (post.author_id == request.user.id or request.user.is_staff):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
            return redirect('stories:post_list')
        post.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'post_id': post_id})
        return redirect('stories:post_list')


@method_decorator(login_required, name='dispatch')
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if not post.allow_comments:
            return JsonResponse({'status': 'error', 'message': 'Comments are disabled for this post'}, status=400)
            
        text = request.POST.get('text', '').strip()
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)
            
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            text=text
        )
        
        # Render the comment to HTML
        html = render_to_string('stories/partials/comment.html', {'comment': comment})
        
        return JsonResponse({
            'status': 'success',
            'html': html,
            'comment_count': post.comment_set.count()
        })


class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    form_class = StoryForm
    template_name = 'stories/story_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Determine the story type based on what was provided
        if form.cleaned_data.get('image'):
            form.instance.story_type = 'image'
        elif form.cleaned_data.get('video'):
            form.instance.story_type = 'video'
        else:
            form.instance.story_type = 'text'
            
        response = super().form_valid(form)
        messages.success(self.request, 'Your story has been posted successfully!')
        return response


class StoryViewView(LoginRequiredMixin, View):
    def post(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)
        
        # Check if the story has already been viewed by this user
        if not story.views.filter(id=request.user.id).exists():
            story.views.add(request.user)
            
        return JsonResponse({'status': 'success'})


class StoryDetailView(LoginRequiredMixin, DetailView):
    model = Story
    template_name = 'stories/story_detail.html'
    context_object_name = 'story'
    
    def get_queryset(self):
        return Story.objects.filter(expiry__gt=timezone.now())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        
        # Mark the story as viewed by the current user
        if not story.views.filter(id=self.request.user.id).exists():
            story.views.add(self.request.user)
            
        # Get other active stories from the same user
        context['user_stories'] = Story.objects.filter(
            user=story.user,
            expiry__gt=timezone.now()
        ).exclude(id=story.id).order_by('created_at')
        
        return context
