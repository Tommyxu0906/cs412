from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import *


class ShowHomeView(View):
    def get(self, request, *args, **kwargs):
        listings = Listing.objects.all()
        return render(request, 'project/home.html', {'listings': listings})

class ShowListingPageView(DetailView):
    model = Listing
    template_name = 'project/listing_detail.html'  # The template for displaying a single listing
    context_object_name = 'listing'  # Use 'listing' as the variable name in the template