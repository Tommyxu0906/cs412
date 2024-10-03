# tell the admin we want to administer these models
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Profile)

