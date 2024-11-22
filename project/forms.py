from django import forms
from django.contrib.auth.models import User
from .models import *
from datetime import datetime


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
    cardholder_name = forms.CharField(
        label='Cardholder Name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    card_number = forms.CharField(
        label='Card Number',
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}),
    )
    expiry_date = forms.CharField(
        label='Expiry Date (MM/YY)',
        max_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}),
    )
    card_type = forms.ChoiceField(
        label='Card Type',
        choices=[('Visa', 'Visa'), ('MasterCard', 'MasterCard'), ('Amex', 'American Express')],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')

        # Ensure the card number is numeric and exactly 16 digits
        if len(card_number) != 16 or not card_number.isdigit():
            raise forms.ValidationError("Card number must be exactly 16 digits.")

        # Optional: Validate card prefixes for card type
        if self.cleaned_data.get('card_type') == 'Visa' and not card_number.startswith('4'):
            raise forms.ValidationError("Visa card numbers must start with '4'.")
        elif self.cleaned_data.get('card_type') == 'MasterCard' and not (51 <= int(card_number[:2]) <= 55):
            raise forms.ValidationError("MasterCard numbers must start with a number between 51 and 55.")
        elif self.cleaned_data.get('card_type') == 'Amex' and not card_number.startswith(('34', '37')):
            raise forms.ValidationError("American Express numbers must start with '34' or '37'.")

        return card_number

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')

        # Check format MM/YY
        if len(expiry_date) != 5 or expiry_date[2] != '/':
            raise forms.ValidationError("Expiry date must be in MM/YY format.")

        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int('20' + year)  # Convert YY to YYYY
        except ValueError:
            raise forms.ValidationError("Expiry date must be in MM/YY format.")

        # Check for valid month
        if month < 1 or month > 12:
            raise forms.ValidationError("Expiry month must be between 01 and 12.")

        # Check if expiry date is in the future
        now = datetime.now()
        if year < now.year or (year == now.year and month < now.month):
            raise forms.ValidationError("Expiry date cannot be in the past.")

        return expiry_date

    def clean_cardholder_name(self):
        cardholder_name = self.cleaned_data.get('cardholder_name')

        # Ensure the cardholder name is not empty and only contains letters and spaces
        if not cardholder_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Cardholder name can only contain letters and spaces.")

        return cardholder_name
