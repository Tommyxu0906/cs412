#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView
# Create your views here.

class ShowAllProfilesView(ListView):
    """creates view for minifb"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'
