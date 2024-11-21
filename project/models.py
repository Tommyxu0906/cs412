from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Listing(models.Model):
    name = models.CharField(max_length=200) # Name of the item
    description = models.TextField() # Description of the item
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price of the item
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True) # Image of the item
    category = models.CharField(max_length=100) # Category the item belongs to
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp for when the item was listed
    expires_at = models.DateTimeField() # Expiration timestamp for the listing
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")  # Link to User
    sold = models.BooleanField(default=False)  # Track sold status

    def clean(self):
        # Validate the price field
        if self.price is None:
            raise ValidationError("There's a problem with your listing")
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.price > 99999:
            raise ValidationError("Price cannot exceed 99999.")

    def save(self, *args, **kwargs):
        # Call the clean method to validate the model before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')],
        default='Pending'
    )

    def __str__(self):
        return f"Order {self.id}: {self.listing.name} by {self.buyer.username}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_price(self):
        return sum(item.listing.price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing.name} in {self.cart.user.username}'s cart"