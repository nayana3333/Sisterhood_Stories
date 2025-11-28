from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def default_expiry():
    return timezone.now() + timezone.timedelta(hours=24)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    file = models.FileField(upload_to='post_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shared_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    is_anonymous = models.BooleanField(default=False)
    pseudonym = models.CharField(max_length=80, blank=True)
    allow_comments = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

class Story(models.Model):
    STORY_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_type = models.CharField(max_length=10, choices=STORY_TYPES, default='text')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='stories/images/', blank=True, null=True)
    video = models.FileField(upload_to='stories/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(default=default_expiry)
    views = models.ManyToManyField(User, related_name='viewed_stories', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"
