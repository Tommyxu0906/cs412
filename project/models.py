from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    # Establishes a one-to-one relationship with the User model. This is useful for extending the default User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField()  # Stores the address of the user as a text field.
    phone_number = models.CharField(max_length=15)  # Stores the phone number, limited to 15 characters.
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Optional field for user's profile image.

    def __str__(self):
        return self.user.username  # Returns the username when the model instance is called.

class Listing(models.Model):
    # Defines properties for a marketplace listing.
    name = models.CharField(max_length=200) # Name of the item.
    description = models.TextField() # Description of the item.
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price of the item, with validation in clean method.
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True) # Optional image for the item.
    category = models.CharField(max_length=100) # Category the item belongs to.
    created_at = models.DateTimeField(auto_now_add=True) # Records when the listing was created.
    expires_at = models.DateTimeField() # When the listing expires.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")  # The user who posted the listing.
    sold = models.BooleanField(default=False)  # Indicates if the item has been sold.
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the item available.

    def clean(self):
        # Validates the price of the listing.
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.price > 99999:
            raise ValidationError("Price cannot exceed 99999.")

    def save(self, *args, **kwargs):
        # Calls the clean method before saving to ensure data integrity.
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

class Order(models.Model):
    # Manages orders placed by users for listings.
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Quantity ordered.
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total price for the order.
    delivery_address = models.TextField(blank=True, null=True)  # Optional delivery address.
    created_at = models.DateTimeField(auto_now_add=True)  # Records when the order was created.
    status = models.CharField(
        max_length=50, 
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')],
        default='Pending'
    )  # Status of the order.

    def __str__(self):
        return f"Order {self.id}: {self.listing.name} (x{self.quantity}) by {self.buyer.username}"

class Cart(models.Model):
    # Represents a shopping cart for a user.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)  # Records when the cart was created.

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_price(self):
        # Calculates the total price of all items in the cart that have not been sold.
        return sum(item.listing.price * item.quantity for item in self.items.filter(listing__sold=False))

class CartItem(models.Model):
    # Represents an item in a shopping cart.
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Quantity of this item in the cart.

    def __str__(self):
        return f"{self.listing.name} (x{self.quantity}) in {self.cart.user.username}'s cart"

    @property
    def total_price(self):
        """Calculate the total price for this cart item."""
        return self.listing.price * self.quantity

class CreditCard(models.Model):
    # Stores credit card information with sensitive data minimally stored.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_cards')
    cardholder_name = models.CharField(max_length=100)  # Name on the card.
    card_number_last4 = models.CharField(max_length=4)  # Last four digits of the card number.
    expiry_date = models.CharField(max_length=5)  # Expiry date in MM/YY format.
    card_type = models.CharField(max_length=20, choices=[('Visa', 'Visa'), ('MasterCard', 'MasterCard'), ('Amex', 'American Express')])

    def __str__(self):
        return f"{self.card_type} ending in {self.card_number_last4}"
