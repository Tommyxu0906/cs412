#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView
from django.views.generic import DetailView
# Create your views here.

class ShowAllProfilesView(ListView):
    """creates view for minifb"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    '''creates view for individual profile'''
    model = Profile
    template_name = 'mini_fb/show_profile_page.html'
    context_object_name = 'profile'
