from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', ShowHomeView.as_view(), name='home'),
    path('listing/<int:pk>/', ShowListingPageView.as_view(), name='listing_detail'),
    path('user/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='project/logged_out.html'), name='logout'),
    path('register/', register, name='register'),
]
