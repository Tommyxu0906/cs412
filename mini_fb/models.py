# mini_fb/models.py
# define the data objects in mini_fb project
from django.db import models

# Create your models here.

class Profile(models.Model):
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
