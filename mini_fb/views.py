#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import DetailView
from django.urls import reverse
from django.views.generic.edit import CreateView
from .forms import CreateProfileForm
from django.shortcuts import get_object_or_404
from .models import StatusMessage, Profile
from .forms import CreateStatusMessageForm
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

class CreateProfileView(CreateView):
    # creates view for creating new profile
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class CreateStatusMessageView(CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'
    
    # Add the profile object to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        context['profile'] = profile
        return context

    # Attach the profile to the status message before saving
    def form_valid(self, form):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        form.instance.profile = profile
        return super().form_valid(form)


    # Redirect to the profile page after the form is successfully submitted
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
