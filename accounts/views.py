from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from stories.models import Post
from .forms import RegisterForm
from .models import Profile

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully! Please login to continue.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        ctx = {
            'my_posts': Post.objects.filter(author=request.user).order_by('-created_at')
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        # Handle profile updates
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        if 'about' in request.POST:
            profile.about = request.POST.get('about', '')
        if 'interests' in request.POST:
            profile.interests = request.POST.get('interests', '')
        if 'bio' in request.POST:
            profile.bio = request.POST.get('bio', '')
        if 'display_name' in request.POST:
            parts = request.POST.get('display_name', '').split(' ', 1)
            user.first_name = parts[0] if parts else ''
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save()
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/delete_account_confirm.html'
    success_url = reverse_lazy('home')
    
    def get_object(self, queryset=None):
        return self.request.user
        
    def delete(self, request, *args, **kwargs):
        # Delete all posts by this user first
        Post.objects.filter(author=request.user).delete()
        
        # Logout the user before deleting the account
        from django.contrib.auth import logout
        logout(request)
        
        # Delete the user account
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Your account and all associated data have been successfully deleted.')
        return response
