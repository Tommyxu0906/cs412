# blog/models.py
# define the data objects in our project
from django.db import models

# Create your models here.

class Article(models.Model):
    '''encapsulate the idea of one article by some author'''
    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True)
    
    def __str__(self):
        return f'{self.title} by {self.author}'


