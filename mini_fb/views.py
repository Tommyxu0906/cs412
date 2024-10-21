#mini_fb/views.py
#import modules for the views
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import *
from .forms import *
from django.utils import timezone

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
        # Get the profile using the primary key from the URL
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])

        # Save the form but do not commit yet, to add the profile manually
        sm = form.save(commit=False)
        sm.profile = profile  # Associate the status message with the profile
        sm.save()

        files = self.request.FILES.getlist('files')

        for file in files:
            image = Image(
                image_file=file,
                status_message=sm,  # Associate with the newly created status message
                uploaded_at=timezone.now()
            )
            image.save()

        # Redirect to the profile page or any other relevant page
        return redirect('show_profile', pk=profile.pk)

    # Redirect to the profile page after the form is successfully submitted
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})
    
class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'
    
    # Redirect to the profile page after a successful form submission
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    # Redirect to the profile page after a successful delete
    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm 
    template_name = 'mini_fb/update_status_form.html'

    # Redirect to the profile page after a successful update
    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})