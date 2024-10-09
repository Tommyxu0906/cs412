# tell the admin we want to administer these models
from django.contrib import admin

# Register your models here.
from .models import *

'''registers models to admin'''
admin.site.register(Profile)
admin.site.register(StatusMessage)

