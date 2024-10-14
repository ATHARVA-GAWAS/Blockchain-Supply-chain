from django import forms
from .models import Transaction, Crop

class LoginForm(forms.Form):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('distributor', 'Distributor'),
        ('vendor', 'Vendor'),
        ('wholesaler', 'Wholesaler'),
        ('retailer', 'Retailer'),
        ('consumer', 'Consumer'),
    ]
    
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['crop', 'quantity', 'price']  # Ensure 'price' is included if it’s a field in the Transaction model.

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop  # Ensure the Crop model is correctly referenced
        fields = ['product_id', 'name', 'description', 'price']  # Include relevant fields from the Crop model
