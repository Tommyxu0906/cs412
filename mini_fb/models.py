# mini_fb/models.py
# define the data objects in mini_fb project
from django.db import models
from django.utils import timezone
# Create your models here.


class Profile(models.Model):
    '''profile class defines attributes of each profile'''
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_status_messages(self):
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')

class StatusMessage(models.Model):
    '''status message class for mini_fb'''
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}: {self.message[:20]}..."
