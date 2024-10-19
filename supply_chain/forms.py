# supply_chain/forms.py
from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'quantity', 'current_stage']

# supply_chain/forms.py
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Crop

class CropPriceUpdateForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['price']  # Only allow editing of the price field

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')