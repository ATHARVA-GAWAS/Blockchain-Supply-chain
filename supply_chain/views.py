from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User, Crop, Transaction
from .forms import TransactionForm, LoginForm, CropForm
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin

# Login view for all users
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']  # Get the selected role
            user = authenticate(request, username=username, password=password)
            if user is not None and user.role == role:  # Ensure the user's role matches the selected role
                login(request, user)
                return redirect(f'{role}/dashboard/')  # Redirect to the corresponding dashboard
            else:
                form.add_error(None, 'Invalid username, password, or role.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

# Farmer Dashboard
@login_required
def farmer_dashboard(request):
    if request.user.role != 'farmer':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    crops = Crop.objects.filter(owner=request.user)
    return render(request, 'farmer_dashboard.html', {'crops': crops})

# Distributor Dashboard
@login_required
def distributor_dashboard(request):
    if request.user.role != 'distributor':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'distributor_dashboard.html', {'transactions': transactions})

# Vendor Dashboard
@login_required
def vendor_dashboard(request):
    if request.user.role != 'vendor':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'vendor_dashboard.html', {'transactions': transactions})

# Wholesaler Dashboard
@login_required
def wholesaler_dashboard(request):
    if request.user.role != 'wholesaler':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'wholesaler_dashboard.html', {'transactions': transactions})

# Retailer Dashboard
@login_required
def retailer_dashboard(request):
    if request.user.role != 'retailer':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'retailer_dashboard.html', {'transactions': transactions})

# Consumer Dashboard
@login_required
def consumer_dashboard(request):
    if request.user.role != 'consumer':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'consumer_dashboard.html', {'transactions': transactions})

# Create Transaction View
@login_required
def create_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.buyer = request.user  # Set the buyer to the logged-in user
            crop = get_object_or_404(Crop, id=request.POST.get('crop_id'))
            transaction.crop = crop
            base_price = crop.price  # Assuming the Crop model has a price field
            transaction.price = base_price * 1.15  # Capping profit margin at 15%
            transaction.save()
            return redirect('transaction_list')  # Redirect to the transaction list after saving

    else:
        form = TransactionForm()
    
    crops = Crop.objects.all()  # Provide a list of crops for selection in the form
    return render(request, 'create_transaction.html', {'form': form, 'crops': crops})

# Sell Crop View (common for all roles)
@login_required
def sell_crop_view(request):
    if request.method == 'POST':
        crop_id = request.POST.get('crop_id')
        crop = get_object_or_404(Crop, id=crop_id)

        if crop.owner != request.user:
            return HttpResponseForbidden("You do not own this crop.")

        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.crop = crop
            transaction.buyer = request.user  # Set the buyer to the logged-in user
            base_price = crop.price  # Assuming the Crop model has a price field
            # Calculate the selling price with a capped profit margin of 15%
            selling_price = base_price * 1.15
            transaction.price = selling_price
            transaction.save()
            return redirect('transaction_list')

    else:
        form = TransactionForm()

    crops = Crop.objects.filter(owner=request.user)  # Only allow selling owned crops
    return render(request, 'sell_crop.html', {'form': form, 'crops': crops})

# Transaction List View for each role
@login_required
def transaction_list_view(request):
    transactions = Transaction.objects.all()
    return render(request, 'transaction_list.html', {'transactions': transactions})

# Logout view (if needed)
@login_required
def logout_view(request):
    # Add logout logic if you are using Django's built-in logout
    pass



class RoleRequiredMixin(UserPassesTestMixin):
    """A mixin to check if the user has the required role."""
    def test_func(self):
        return self.request.user.role in ['farmer', 'distributor', 'vendor', 'wholesaler', 'retailer']

@login_required
def create_crop(request):
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.save()  # Save the crop to the database
            
            # Redirect to the respective dashboard based on user role
            if request.user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif request.user.role == 'distributor':
                return redirect('distributor_dashboard')
            elif request.user.role == 'vendor':
                return redirect('vendor_dashboard')
            elif request.user.role == 'wholesaler':
                return redirect('wholesaler_dashboard')
            elif request.user.role == 'retailer':
                return redirect('retailer_dashboard')
            else:
                return redirect('consumer_dashboard')  # Fallback, though consumers can't create crops
    else:
        form = CropForm()
    
    return render(request, 'create_crop.html', {'form': form})

# Alternatively, using a class-based view
class CreateCropView(RoleRequiredMixin, View):
    def get(self, request):
        form = CropForm()
        return render(request, 'create_crop.html', {'form': form})

    def post(self, request):
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.save()  # Save the crop to the database
            return redirect('farmer_dashboard')  # Redirect to the farmer dashboard or another appropriate page
        return render(request, 'create_crop.html', {'form': form})