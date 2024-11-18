from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileForm

def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the User object
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Save the Profile object
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "Your account has been created successfully!")
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()

    return render(request, 'project/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


class ShowHomeView(View):
    def get(self, request, *args, **kwargs):
        listings = Listing.objects.all()
        return render(request, 'project/home.html', {'listings': listings})

class ShowListingPageView(DetailView):
    model = Listing
    template_name = 'project/listing_detail.html'  # The template for displaying a single listing
    context_object_name = 'listing'  # Use 'listing' as the variable name in the template



class UserProfileView(DetailView):
    model = User
    template_name = 'project/profile.html'
    context_object_name = 'user'
