# mini_fb/models.py
# define the data objects in mini_fb project
from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.

class Profile(models.Model):
    '''profile class defines attributes of each profile'''
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)
    '''str method'''
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_status_messages(self):
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    #gets friends for each profile
    def get_friends(self):
        friends_as_profile1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends_as_profile2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)
        friend_ids = list(friends_as_profile1) + list(friends_as_profile2)
        return Profile.objects.filter(id__in=friend_ids)
    
    def add_friend(self, other):
        # Check if the friend relationship already exists
        if not Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | 
            models.Q(profile1=other, profile2=self)
        ).exists():
            # Create a new Friend instance
            Friend.objects.create(profile1=self, profile2=other, timestamp=timezone.now())

    def get_friend_suggestions(self):
        current_friends = self.get_friends()
        return Profile.objects.exclude(
            models.Q(id=self.id) | models.Q(id__in=[friend.id for friend in current_friends])
        )
    
    def get_news_feed(self):
        # Get status messages for this profile
        own_statuses = StatusMessage.objects.filter(profile=self)

        # Get status messages for friends
        friends = self.get_friends()
        friends_statuses = StatusMessage.objects.filter(profile__in=friends)

        # Combine and sort by timestamp, most recent first
        all_statuses = own_statuses.union(friends_statuses).order_by('-timestamp')
        return all_statuses



class StatusMessage(models.Model):
    '''status message class for mini_fb'''
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}: {self.message[:20]}..."
    
    '''method to get image'''
    def get_images(self):
        return Image.objects.filter(status_message=self)

#image model
class Image(models.Model):
    image_file = models.ImageField(upload_to='images/')
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Image for {self.status_message}"

class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends1')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends2')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}'