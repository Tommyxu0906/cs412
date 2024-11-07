# voter_analytics/urls.py
from django.urls import path
from .views import VoterListView, VoterDetailView

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),  # ListView for all voters
    path('voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),  # DetailView for single voter
]
