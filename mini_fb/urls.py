#mini_fb/urls.py imports modules
from django.urls import path
from .views import ShowAllProfilesView, ShowProfilePageView, CreateProfileView

urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
]
