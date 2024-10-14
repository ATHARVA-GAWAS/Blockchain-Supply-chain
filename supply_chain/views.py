
from .models import Transaction
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Crop, Transaction, Block
from .blockchain import Blockchain
from django.contrib.auth.models import User

# Create your views here.
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

from django.shortcuts import render, redirect
from .models import Crop
from .blockchain import Blockchain  # Import your blockchain class

blockchain = Blockchain()  # Initialize your blockchain

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Change this to your login URL name
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# In supply_chain/views.py

def home(request):
    return render(request, 'home.html')  # Assuming you have a template named 'home.html'

def transaction_history(request):
    transactions = Transaction.objects.filter(buyer=request.user) | Transaction.objects.filter(seller=request.user)
    return render(request, 'transaction_history.html', {'transactions': transactions})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'FARMER':
        crops = Crop.objects.filter(current_owner=user)
        return render(request, 'farmer_dashboard.html', {'crops': crops})
    elif user.role == 'DISTRIBUTOR':
        crops = Crop.objects.filter(current_owner=user)
        return render(request, 'distributor_dashboard.html', {'crops': crops})
    elif user.role == 'CONSUMER':
        crops = Crop.objects.all()  # Consumers can view all available crops
        return render(request, 'consumer_dashboard.html', {'crops': crops})
    else:
        return redirect('list_crops')



# Initialize Blockchain instance
blockchain = Blockchain()

@login_required
def list_crops(request):
    if request.method == 'POST':
        # Using .get() method to prevent MultiValueDictKeyError
        crop_name = request.POST.get('name')
        quantity_str = request.POST.get('quantity')
        price_str = request.POST.get('price')

        # Validating the input
        if crop_name and quantity_str and price_str:
            try:
                quantity = float(quantity_str)
                price = float(price_str)

                # Creating the crop instance
                crop = Crop.objects.create(
                    name=crop_name,
                    quantity=quantity,
                    price=price,
                    current_owner=request.user,
                    current_stage='Listed by Farmer'
                )
                crop.save()

                # Create a transaction and add it to the blockchain
                transaction = {
                    'crop_name': crop_name,
                    'quantity': quantity,
                    'price': price,
                    'owner': request.user.username,
                    'stage': 'Listed by Farmer'
                }
                blockchain.add_transaction(transaction)

                # Create a new block to store the transaction
                blockchain.mine_block()

                messages.success(request, f"Crop '{crop_name}' listed successfully and added to the blockchain!")
            except ValueError:
                messages.error(request, "Invalid quantity or price. Please enter numeric values.")
        else:
            messages.error(request, "All fields are required.")

        return redirect('list_crops')

    # Fetching all crops to display
    crops = Crop.objects.all()
    return render(request, 'list_crops.html', {'crops': crops})


# def buy_crop(request, crop_id):
#     crop = Crop.objects.get(id=crop_id)
#     if request.method == 'POST':
#         buyer = request.user
#         quantity = float(request.POST['quantity'])
#         price = float(request.POST['price'])

#         # Create a transaction record
#         transaction = Transaction.objects.create(
#             buyer=buyer,
#             seller=crop.current_owner,
#             crop=crop,
#             quantity=quantity,
#             price=price
#         )

#         # Update crop ownership and stage
#         crop.current_owner = buyer
#         crop.current_stage = 'Purchased by Distributor'
#         crop.save()

#         # Add transaction to blockchain
#         transaction_data = {
#             'buyer': buyer.username,
#             'seller': crop.current_owner.username,
#             'crop_name': crop.name,
#             'quantity': quantity,
#             'price': price
#         }
#         blockchain.add_block(transaction_data)

#         return redirect('list_crops')

#     return render(request, 'buy_crop.html', {'crop': crop})
@login_required
def buy_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)

    if request.method == 'POST':
        # Allow only distributors to buy crops
        if request.user.role != 'distributor' or request.user.role != 'consumer':
            messages.error(request, "Only distributors and consumers can buy crops.")
            return redirect('list_crops')

        if crop.status == 'listed' and crop.quantity > 0:
            # Update crop details
            crop.current_owner = request.user
            crop.status = 'sold'
            crop.quantity -= 1

            # Create a blockchain transaction (pseudo-code)
            transaction_index = blockchain.new_transaction(
                sender=crop.current_owner.username,
                recipient=request.user.username,
                crop_name=crop.name,
                quantity=1,
                price=crop.price
            )
            crop.transaction_hash = f'Transaction #{transaction_index}'
            crop.save()

            # Mine the new block (pseudo-code)
            blockchain.create_block(proof=100)
            messages.success(request, f"You have purchased {crop.name}!")
            return redirect('transaction_history')

    return render(request, 'buy_crop.html', {'crop': crop})

@login_required
def sell_crop(request):
    if request.method == 'POST':
        # Allow only distributors to sell crops
        if request.user.role != 'distributor':
            messages.error(request, "Only distributors can sell crops.")
            return redirect('list_crops')

        crop_name = request.POST['name']
        quantity = float(request.POST['quantity'])
        price = float(request.POST['price'])

        crop = Crop.objects.create(
            name=crop_name,
            quantity=quantity,
            price=price,
            current_owner=request.user,
            status='listed',
            current_stage='Listed by Distributor'
        )

        # Create a blockchain transaction (pseudo-code)
        transaction_index = blockchain.new_transaction(
            sender=request.user.username,
            recipient='Market',
            crop_name=crop.name,
            quantity=crop.quantity,
            price=crop.price
        )
        crop.transaction_hash = f'Transaction #{transaction_index}'
        crop.save()

        messages.success(request, f"You have listed {crop.name} for sale!")
        return redirect('transaction_history')

    return render(request, 'sell_crop.html')

@login_required
def blockchain_status(request):
    chain = blockchain.get_chain()
    return render(request, 'blockchain_status.html', {'chain': chain})

from django.shortcuts import redirect

def profile_view(request):
    # Redirect users to their dashboard or home page after login
    return redirect('dashboard')  # Replace 'dashboard' with the name of the view you want to redirect to

# def trace_crop(request, crop_id):
#     crop = get_object_or_404(Crop, id=crop_id)
#     return render(request, 'trace_crop.html', {'crop': crop})

def trace_crop(request, crop_id):
    block = blockchain.trace_crop(crop_id)
    return render(request, 'trace_crop.html', {'block': block})

@login_required
def user_logout(request):
    # logout(request)  # This will log out the user
    return redirect('dashboard')   # Redirect to a success page

def logout_success(request):
    return redirect('dashboard')

# views.py
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('dashboard')  # Redirect to the desired page after login
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
