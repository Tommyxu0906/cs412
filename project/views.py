from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import ValidationError

class CreateListingView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'project/create_listing.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
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

class PlaceOrderView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        # Fetch the listing to display the order confirmation page
        listing = get_object_or_404(Listing, pk=pk)

        # Prevent self-purchase
        if request.user == listing.user:
            return HttpResponseForbidden("You cannot purchase your own listing.")

        return render(request, 'project/place_order.html', {'listing': listing})

    def post(self, request, pk, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=pk)

        # Prevent self-purchase
        if request.user == listing.user:
            return HttpResponseForbidden("You cannot purchase your own listing.")

        # Check if the listing is already sold
        if listing.sold:
            return HttpResponseForbidden("This listing has already been sold.")

        # Mark the listing as sold and create the order
        order, created = Order.objects.get_or_create(
            buyer=request.user,
            seller=listing.user,
            listing=listing,
        )
        listing.sold = True
        listing.save()

        # Redirect to the order confirmation or history page
        return redirect('order_history')  # Replace 'order_history' with the appropriate URL name
    
class OrderHistoryView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Get all orders of the logged-in user
        orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
        return render(request, 'project/order_history.html', {'orders': orders})
    
class ManageListingsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Fetch listings created by the logged-in user
        listings = Listing.objects.filter(user=request.user).order_by('-created_at')

        # Fetch orders for these listings (if any)
        orders = Order.objects.filter(seller=request.user).select_related('buyer__profile', 'listing')

        # Pass both listings and orders to the template
        return render(request, 'project/manage_listings.html', {
            'listings': listings,
            'orders': orders,
        })



class EditListingView(LoginRequiredMixin, UpdateView):
    model = Listing
    fields = ['name', 'description', 'price', 'image', 'category', 'expires_at']
    template_name = 'project/edit_listing.html'
    success_url = '/listings/manage/'

    def get_queryset(self):
        # Ensure the user can only edit their own listings
        return Listing.objects.filter(user=self.request.user)

class DeleteListingView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=pk)
        # Ensure the user can only delete their own listings
        if listing.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this listing.")
        listing.delete()
        return redirect('manage_listings')

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, listing_id, *args, **kwargs):
        listing = get_object_or_404(Listing, id=listing_id)

        # Prevent adding sold items
        if listing.sold:
            return HttpResponseForbidden("This item has already been sold.")
        
        # Prevent self-purchase
        if request.user == listing.user:
            return HttpResponseForbidden("You cannot purchase your own listing.")
        
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Add item to the cart if not already present
        if not CartItem.objects.filter(cart=cart, listing=listing).exists():
            CartItem.objects.create(cart=cart, listing=listing)

        return redirect('cart')


class ViewCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        return render(request, 'project/cart.html', {'cart': cart})

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return redirect('cart')

class CheckoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Get the cart for the logged-in user
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.all()

        if not items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        # Process each cart item
        for item in items:
            listing = item.listing

            # Ensure the listing has a valid seller
            if not listing.user:
                messages.error(request, f"Listing {listing.name} does not have a valid seller.")
                return redirect('cart')

            # Mark the listing as sold
            listing.sold = True
            listing.save()

            # Create an order
            Order.objects.create(
                buyer=request.user,
                seller=listing.user,  # Set the seller explicitly
                listing=listing,
            )

        # Clear the cart after checkout
        items.delete()

        messages.success(request, "Checkout successful! Your order has been placed.")
        return redirect('order_history')  # Redirect to the user's order history

class UpdateOrderStatusView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, id=pk, seller=request.user)
        status = request.POST.get('status')

        if status not in ['Pending', 'Paid', 'Shipped', 'Delivered']:
            return HttpResponseForbidden("Invalid status value.")

        order.status = status
        order.save()

        # Notify the buyer (if needed)
        # Example: Send an email or add a notification

        messages.success(request, f"Order status updated to {status}.")
        return redirect('manage_listings')