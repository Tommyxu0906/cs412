from django import forms
from django.contrib.auth.models import User
from .models import *

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'phone_number', 'profile_image']

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['name', 'description', 'price', 'image', 'category', 'expires_at']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price cannot be empty.")
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        if price > 99999:
            raise forms.ValidationError("Price cannot exceed 99999.")
        return price
    
class CreditCardForm(forms.Form):
    cardholder_name = forms.CharField(label='Cardholder Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    card_number = forms.CharField(label='Card Number', max_length=16, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
    expiry_date = forms.CharField(label='Expiry Date (MM/YY)', max_length=5, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    card_type = forms.ChoiceField(label='Card Type', choices=[('Visa', 'Visa'), ('MasterCard', 'MasterCard'), ('Amex', 'American Express')], widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        if len(card_number) != 16 or not card_number.isdigit():
            raise forms.ValidationError("Card number must be 16 digits.")
        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if len(expiry_date) != 5 or expiry_date[2] != '/':
            raise forms.ValidationError("Expiry date must be in MM/YY format.")
        return expiry_date