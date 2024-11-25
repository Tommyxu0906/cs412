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
    path('create-listing/', CreateListingView.as_view(), name='create_listing'),
    path('order/place/<int:pk>/', PlaceOrderView.as_view(), name='place_order'),
    path('order/complete/<int:pk>/', CompleteOrderView.as_view(), name='complete_order'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('listings/manage/', ManageListingsView.as_view(), name='manage_listings'),
    path('listings/edit/<int:pk>/', EditListingView.as_view(), name='edit_listing'),
    path('listings/delete/<int:pk>/', DeleteListingView.as_view(), name='delete_listing'),
    path('cart/add/<int:listing_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', ViewCartView.as_view(), name='cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/update/<int:pk>/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('credit-cards/', ManageCreditCardsView.as_view(), name='manage_credit_cards'),
    path('credit-cards/delete/<int:pk>/', DeleteCreditCardView.as_view(), name='delete_credit_card'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/<int:pk>/', CheckoutView.as_view(), name='checkout_single'),
    path('checkout/cart/', CartCheckoutView.as_view(), name='checkout_cart'),
    

]
