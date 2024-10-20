# supply_chain/forms.py
from django import forms
from .models import Crop
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    # allowed_users = forms.ModelMultipleChoiceField(
    #     queryset=CustomUser.objects.all(),  # Filter for customers or specific roles
    #     widget=forms.CheckboxSelectMultiple,  # You can also use a select widget
    #     required=False
    # )

    class Meta:
        model = Crop
        fields = ['name', 'quantity', 'price']

class CropPriceUpdateForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['price']  # Only allow editing of the price field

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')