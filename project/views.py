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
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash

# Method for handling register
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
    
class CreateListingView(LoginRequiredMixin, CreateView):
    #View for creating a new listing
    model = Listing
    form_class = ListingForm
    template_name = 'project/create_listing.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ShowListingPageView(DetailView):
    model = Listing
    template_name = 'project/listing_detail.html'  # The template for displaying a single listing
    context_object_name = 'listing'  # Use 'listing' as the variable name in the template

class UserProfileView(DetailView):
    model = User
    template_name = 'project/profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the logged-in user is the owner of the profile
        context['is_owner'] = self.request.user.is_authenticated and self.request.user == self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        # Ensure the request user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to update your profile.")
            return redirect('login')

        # Get the profile being accessed
        user = self.get_object()
        
        # Ensure the logged-in user matches the profile owner
        if request.user != user:
            messages.error(request, "You are not authorized to edit this profile.")
            return redirect('user_profile', pk=user.pk)

        # Handle profile updates
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        username = request.POST.get('username', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '').strip()

        # Validation checks
        if not email:
            messages.error(request, "Email is required.")
            return redirect('user_profile', pk=user.pk)

        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('user_profile', pk=user.pk)

        # Update the user's profile
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        if password:
            user.password = make_password(password)
            update_session_auth_hash(request, user)  # Only keep session for the logged-in user
        user.save()

        # Update the user profile
        profile = user.profile
        profile.address = address
        profile.phone_number = phone_number
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile', pk=user.pk)

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
        orders = Order.objects.filter(buyer=request.user).select_related('listing', 'seller').order_by('-created_at')
        return render(request, 'project/order_history.html', {'orders': orders})
    
class ManageListingsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Fetch listings created by the logged-in user
        listings = Listing.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'project/manage_listings.html', {
            'listings': listings,
        })

class ManageSalesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Fetch all orders where the logged-in user is the seller
        orders = Order.objects.filter(seller=request.user).select_related('listing', 'buyer__profile').order_by('-created_at')

        return render(request, 'project/manage_sales.html', {
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
        
        # Validate the quantity
        try:
            quantity = int(request.POST.get('quantity', 1))  # Default to 1 if no quantity is provided
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect('listing_detail', pk=listing.id)

        if quantity < 1 or quantity > listing.quantity:
            messages.error(request, "Invalid quantity selected.")
            return redirect('listing_detail', pk=listing.id)
        
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, listing=listing)

        if not created:
            # Update the quantity if already in the cart
            new_quantity = cart_item.quantity + quantity
            if new_quantity > listing.quantity:
                messages.error(request, "Cannot add more than available quantity.")
                return redirect('cart')
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        messages.success(request, "Item added to cart.")
        return redirect('cart')

    
class ViewCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        unsold_items = cart.items.filter(listing__sold=False).select_related('listing')
        sold_items = cart.items.filter(listing__sold=True).select_related('listing')

        total_price = sum(item.total_price for item in unsold_items)  # Use total_price as a property

        return render(request, 'project/cart.html', {
            'unsold_items': unsold_items,
            'sold_items': sold_items,
            'total_price': total_price,
        })

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return redirect('cart')

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        # Retrieve the listing for single-item checkout
        listing = get_object_or_404(Listing, pk=pk, sold=False)
        quantity = int(request.GET.get('quantity', 1))  # Default to 1 if not provided
        total_price = listing.price * quantity  # Calculate total price

        # Retrieve user's saved credit cards and default address
        credit_cards = CreditCard.objects.filter(user=request.user)
        profile_address = request.user.profile.address

        # Render the checkout template
        return render(request, 'project/checkout.html', {
            'listing': listing,
            'quantity': quantity,
            'total_price': total_price,
            'credit_cards': credit_cards,
            'profile_address': profile_address,
        })

    def post(self, request, pk, *args, **kwargs):
        # Fetch the listing and quantity
        listing = get_object_or_404(Listing, pk=pk, sold=False)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect('checkout_single', pk=pk)

        # Validate quantity
        if quantity < 1 or quantity > listing.quantity:
            messages.error(request, f"Invalid quantity selected. Only {listing.quantity} available.")
            return redirect('checkout_single', pk=pk)

        # Retrieve other submitted data
        delivery_address = request.POST.get('delivery_address', '').strip()
        payment_method = request.POST.get('payment_method')
        cardholder_name = request.POST.get('cardholder_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        expiry_date = request.POST.get('expiry_date', '').strip()
        card_type = request.POST.get('card_type', '').strip()

        # Validate delivery address
        if not delivery_address:
            messages.error(request, "Please provide a delivery address.")
            return self.render_checkout(
                request, pk, delivery_address, quantity, payment_method, cardholder_name, card_number, expiry_date, card_type
            )

        # Handle new card scenario
        if payment_method == "new":
            form = CreditCardForm({
                'cardholder_name': cardholder_name,
                'card_number': card_number,
                'expiry_date': expiry_date,
                'card_type': card_type,
            })
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return self.render_checkout(
                    request, pk, delivery_address, quantity, payment_method, cardholder_name, card_number, expiry_date, card_type
                )

            # Save the new card
            card_number = form.cleaned_data['card_number']
            selected_card = CreditCard.objects.create(
                user=request.user,
                cardholder_name=form.cleaned_data['cardholder_name'],
                card_number_last4=card_number[-4:],  # Store only the last 4 digits
                expiry_date=form.cleaned_data['expiry_date'],
                card_type=form.cleaned_data['card_type'],
            )
        else:
            # Ensure the selected card exists
            try:
                selected_card = CreditCard.objects.get(id=payment_method, user=request.user)
            except CreditCard.DoesNotExist:
                messages.error(request, "Invalid payment method.")
                return self.render_checkout(
                    request, pk, delivery_address, quantity, payment_method, cardholder_name, card_number, expiry_date, card_type
                )

        # Process the order
        with transaction.atomic():
            self.create_order(request, listing, quantity, delivery_address, selected_card)

        messages.success(request, "Order placed successfully!")
        return redirect('order_history')

    def render_checkout(self, request, pk, delivery_address, quantity, payment_method, cardholder_name, card_number, expiry_date, card_type):
        credit_cards = CreditCard.objects.filter(user=request.user)
        profile_address = request.user.profile.address
        listing = get_object_or_404(Listing, pk=pk, sold=False)

        return render(request, 'project/checkout.html', {
            'listing': listing,
            'quantity': quantity,
            'total_price': listing.price * quantity,
            'credit_cards': credit_cards,
            'profile_address': profile_address,
            'delivery_address': delivery_address,
            'payment_method': payment_method,
            'cardholder_name': cardholder_name,
            'card_number': card_number,
            'expiry_date': expiry_date,
            'card_type': card_type,
        })

    def create_order(self, request, listing, quantity, delivery_address, selected_card):
        # Calculate total price
        total_price = quantity * listing.price

        # Create a new order
        Order.objects.create(
            buyer=request.user,
            seller=listing.user,
            listing=listing,
            quantity=quantity,
            total_price=total_price,
            delivery_address=delivery_address,
            status='Pending',
        )

        # Update the listing's quantity
        listing.quantity -= quantity
        if listing.quantity == 0:
            listing.sold = True
        listing.save()

class UpdateOrderStatusView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, id=pk, seller=request.user)
        status = request.POST.get('status')
        next_url = request.POST.get('next', 'manage_sales')

        if status not in ['Pending', 'Paid', 'Shipped', 'Delivered']:
            return HttpResponseForbidden("Invalid status value.")

        order.status = status
        order.save()

        messages.success(request, f"Order status updated to {status}.")
        return redirect(next_url)
    
class ManageCreditCardsView(LoginRequiredMixin, View):
    #Handles adding, deleting credit cards
    def get(self, request, *args, **kwargs):
        cards = CreditCard.objects.filter(user=request.user)
        form = CreditCardForm()
        return render(request, 'project/manage_credit_cards.html', {'cards': cards, 'form': form})

    def post(self, request, *args, **kwargs):
        form = CreditCardForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data['card_number']
            CreditCard.objects.create(
                user=request.user,
                cardholder_name=form.cleaned_data['cardholder_name'],
                card_number_last4=card_number[-4:],  # Store only the last 4 digits
                expiry_date=form.cleaned_data['expiry_date'],
                card_type=form.cleaned_data['card_type'],
            )
            messages.success(request, "Credit card added successfully!")
            return redirect('manage_credit_cards')
        else:
            cards = CreditCard.objects.filter(user=request.user)
            return render(request, 'project/manage_credit_cards.html', {'cards': cards, 'form': form})

class DeleteCreditCardView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        card = get_object_or_404(CreditCard, id=pk, user=request.user)
        card.delete()
        messages.success(request, "Credit card deleted successfully.")
        return redirect('manage_credit_cards')

class CartCheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = request.user.cart  # Retrieve the user's cart

        # Separate unsold and sold items
        unsold_items = cart.items.filter(listing__sold=False).select_related('listing')
        sold_items = cart.items.filter(listing__sold=True).select_related('listing')

        # Get user's saved credit cards and default address
        credit_cards = CreditCard.objects.filter(user=request.user)
        profile_address = request.user.profile.address

        # Calculate total price for unsold items
        total_price = sum(item.quantity * item.listing.price for item in unsold_items)

        return render(request, 'project/checkout_cart.html', {
            'unsold_items': unsold_items,
            'sold_items': sold_items,
            'credit_cards': credit_cards,
            'profile_address': profile_address,
            'unsold_items_total_price': total_price,
        })

    def post(self, request, *args, **kwargs):
        delivery_address = request.POST.get('delivery_address', '').strip()
        payment_method = request.POST.get('payment_method')
        cardholder_name = request.POST.get('cardholder_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        expiry_date = request.POST.get('expiry_date', '').strip()
        card_type = request.POST.get('card_type', '').strip()

        # Validate the delivery address
        if not delivery_address:
            messages.error(request, "Please provide a delivery address.")
            return self.get(request)

        # Handle "Add New Card" scenario
        if payment_method == "new":
            form = CreditCardForm({
                'cardholder_name': cardholder_name,
                'card_number': card_number,
                'expiry_date': expiry_date,
                'card_type': card_type,
            })
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return self.get(request)

            # Save the new card
            card_number = form.cleaned_data['card_number']
            selected_card = CreditCard.objects.create(
                user=request.user,
                cardholder_name=form.cleaned_data['cardholder_name'],
                card_number_last4=card_number[-4:],
                expiry_date=form.cleaned_data['expiry_date'],
                card_type=form.cleaned_data['card_type'],
            )
        else:
            # Validate existing card
            try:
                selected_card = CreditCard.objects.get(id=payment_method, user=request.user)
            except CreditCard.DoesNotExist:
                messages.error(request, "Invalid payment method.")
                return self.get(request)

        # Process cart checkout for unsold items
        cart = request.user.cart
        unsold_items = cart.items.filter(listing__sold=False).select_related('listing')
        if not unsold_items.exists():
            messages.error(request, "Your cart has no items available for checkout.")
            return redirect('cart')

        with transaction.atomic():
            for cart_item in unsold_items:
                listing = cart_item.listing

                # Update quantity of the listing or mark as sold if fully purchased
                if listing.quantity >= cart_item.quantity:
                    listing.quantity -= cart_item.quantity
                    if listing.quantity == 0:
                        listing.sold = True
                    listing.save()

                    # Create an order for each listing
                    Order.objects.create(
                        buyer=request.user,
                        seller=listing.user,
                        listing=listing,
                        quantity=cart_item.quantity,
                        total_price=cart_item.quantity * listing.price,
                        status='Pending',
                        delivery_address=delivery_address,
                    )
                else:
                    messages.error(request, f"Not enough quantity for '{listing.name}'.")

            # Remove processed items from the cart
            unsold_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_history')


class UpdateCartItemQuantityView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        # Validate the new quantity
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect('cart')

        if new_quantity < 1 or new_quantity > cart_item.listing.quantity:
            messages.error(request, f"Quantity must be between 1 and {cart_item.listing.quantity}.")
            return redirect('cart')

        # Update the cart item quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        messages.success(request, "Cart item quantity updated.")
        return redirect('cart')
