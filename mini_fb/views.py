#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView
from django.views.generic import DetailView
from django.urls import reverse
from django.views.generic.edit import CreateView
from .forms import CreateProfileForm
# Create your views here.

class ShowAllProfilesView(ListView):
    """creates view for minifb"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    '''creates view for individual profile'''
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
