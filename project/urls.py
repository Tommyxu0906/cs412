from django.urls import path
from .views import *

urlpatterns = [
    path('', ShowHomeView.as_view(), name='home'),
    path('listing/<int:pk>/', ShowListingPageView.as_view(), name='listing_detail'),
]
