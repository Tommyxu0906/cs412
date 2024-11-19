from django.views import View
from django.views.generic import DetailView, CreateView
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseForbidden

class CreateListingView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['name', 'description', 'price', 'image', 'category', 'expires_at']
    template_name = 'project/create_listing.html'
    success_url = reverse_lazy('home')  # Redirect to home after creation

    def form_valid(self, form):
        # Assign the current user as the owner of the listing
        form.instance.user = self.request.user
        return super().form_valid(form)

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
        query = request.GET.get('q', '')  # Search query
        sort_by = request.GET.get('sort', 'best_match')  # Sorting option
        min_price = request.GET.get('min_price')  # Minimum price filter
        max_price = request.GET.get('max_price')  # Maximum price filter

        if request.user.is_authenticated:
            listings = Listing.objects.filter(sold=False).exclude(user=request.user)
        else:
            listings = Listing.objects.filter(sold=False).all()

        # Search by name, description, or category
        if query:
            listings = listings.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )

        # Filter by price range
        if min_price:
            listings = listings.filter(price__gte=min_price)
        if max_price:
            listings = listings.filter(price__lte=max_price)

        # Sort listings
        if sort_by == 'newly_listed':
            listings = listings.order_by('-created_at')
        elif sort_by == 'ending_soon':
            listings = listings.order_by('expires_at')
        elif sort_by == 'price_low_high':
            listings = listings.order_by('price')
        elif sort_by == 'price_high_low':
            listings = listings.order_by('-price')

        # Count the number of results
        result_count = listings.count()

        return render(request, 'project/home.html', {
            'listings': listings,
            'query': query,
            'sort_by': sort_by,
            'min_price': min_price,
            'max_price': max_price,
            'result_count': result_count,
        })

        

class ShowListingPageView(DetailView):
    model = Listing
    template_name = 'project/listing_detail.html'  # The template for displaying a single listing
    context_object_name = 'listing'  # Use 'listing' as the variable name in the template



class UserProfileView(DetailView):
    model = User
    template_name = 'project/profile.html'
    context_object_name = 'user'


class CompleteOrderView(View):
    def post(self, request, pk, *args, **kwargs):
        # Fetch the order
        order = get_object_or_404(Order, pk=pk)

        # Mark as completed
        order.status = 'Completed'
        order.save()

        # Redirect to a confirmation page or user's orders
        messages.success(request, "Your order has been placed successfully!")
        return redirect('home')

class PlaceOrderView(View):
    def get(self, request, pk, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=pk)

        # Prevent self-purchase
        if request.user == listing.user:
            return HttpResponseForbidden("You cannot purchase your own listing.")

        # Create the order and mark the listing as sold
        order, created = Order.objects.get_or_create(
            buyer=request.user,
            seller=listing.user,
            listing=listing,
        )
        listing.sold = True
        listing.save()

        # Redirect to the order confirmation page
        return render(request, 'project/place_order.html', {'order': order})
    
class OrderHistoryView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Get all orders of the logged-in user
        orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
        return render(request, 'project/order_history.html', {'orders': orders})

