from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Listing(models.Model):
    id = models.AutoField(primary_key=True)  # Unique identifier for the item
    name = models.CharField(max_length=200)  # Name of the item
    description = models.TextField()  # Description of the item
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the item
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)  # Image of the item
    category = models.CharField(max_length=100)  # Category the item belongs to
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the item was listed
    expires_at = models.DateTimeField()  # Expiration timestamp for the listing

    def __str__(self):
        return self.name
