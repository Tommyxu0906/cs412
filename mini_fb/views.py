#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import *
from .forms import *
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView
from django.contrib.auth import login
# Create your views here.

class ShowAllProfilesView(ListView):
    #creates view for minifb
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    #creates view for individual profile
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'
    
    #gets status message and update accordingly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        context['profile'] = profile
        return context
    

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

@method_decorator(csrf_protect, name='dispatch')
class CreateProfileView(FormView):
    template_name = 'mini_fb/create_profile_form.html'
    form_class = CreateProfileForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserCreationForm(request.POST)
        profile_form = CreateProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Prepare Profile
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Debug before saving profile
            print("Profile about to be saved:", profile)
            
            profile.save()
            login(request, user)
            # Redirect to profile
            return redirect('show_profile', pk=profile.pk)
        else:
            if not user_form.is_valid():
                print("User form errors:", user_form.errors)
            if not profile_form.is_valid():
                print("Profile form errors:", profile_form.errors)
            
            return self.form_invalid(profile_form)

    def get_success_url(self):
        return reverse('show_all_profiles')

    
class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    # Add the profile object to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.request.user)
        context['profile'] = profile
        return context

    # Attach the profile to the status message before saving
    def form_valid(self, form):
        # Get the profile using the primary key from the URL
        profile = get_object_or_404(Profile, user=self.request.user)
        sm = form.save(commit=False)
        sm.profile = profile  #
        sm.save()

        files = self.request.FILES.getlist('files')

        for file in files:
            image = Image(
                image_file=file,
                status_message=sm,
                uploaded_at=timezone.now()
            )
            image.save()

        # Redirect to the profile page or any other relevant page
        return redirect('show_profile', pk=profile.pk)

    # Redirect to the profile page after the form is successfully submitted
    def get_success_url(self):
        return reverse('show_profile', user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    # Redirect to the profile page after a successful form submission
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    # Redirect to the profile page after a successful delete
    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm 
    template_name = 'mini_fb/update_status_form.html'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    # Redirect to the profile page after a successful update
    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
class CreateFriendView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        # Get the Profile instances from the URL parameters
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=self.kwargs['other_pk'])
    
        # Add the other profile as a friend
        profile.add_friend(other_profile)

        return redirect('show_profile', pk=profile.pk)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        # Fetch the Profile linked to the current user
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add friend suggestions to the context
        context['friend_suggestions'] = self.get_object().get_friend_suggestions()
        return context

class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_object(self):
        # Get the Profile for the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the profile object to retrieve the news feed
        context['news_feed'] = self.get_object().get_news_feed()
        return context