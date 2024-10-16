
from .models import Crop, Transaction, PurchasedCrop
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Crop, Transaction
from .blockchain import Blockchain, Block
from django.contrib.auth.models import User
from django.contrib.auth import logout


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
        crops = Crop.objects.all()
        return render(request, 'farmer_dashboard.html', {'crops': crops})
    elif user.role == 'DISTRIBUTOR':
        crops = Crop.objects.all()
        return render(request, 'distributor_dashboard.html', {'crops': crops})
    elif user.role == 'CONSUMER':
        crops = Crop.objects.all()  # Consumers can view all available crops
        return render(request, 'consumer_dashboard.html', {'crops': crops})
    else:
        return redirect('list_crops')



# Initialize Blockchain instance
blockchain = Blockchain()

# @login_required
# def list_crops(request):
#     if request.method == 'POST':
#         # Using .get() method to prevent MultiValueDictKeyError
#         crop_name = request.POST.get('name')
#         quantity_str = request.POST.get('quantity')
#         price_str = request.POST.get('price')

#         # Validating the input
#         if crop_name and quantity_str and price_str:
#             try:
#                 quantity = float(quantity_str)
#                 price = float(price_str)

#                 # Creating the crop instance
#                 crop = Crop.objects.create(
#                     name=crop_name,
#                     quantity=quantity,
#                     price=price,
#                     current_owner=request.user,
#                     current_stage='Listed by Farmer'
#                 )
#                 crop.save()

#                 # Get the crop ID after saving the crop
#                 crop_id = crop.id

#                 # Create a transaction and add it to the blockchain
#                 transaction = {
#                     'crop_name': crop_name,
#                     'quantity': quantity,
#                     'price': price,
#                     'owner': request.user.username,
#                     'stage': 'Listed by Farmer'
#                 }
                
#                 # Assuming you have a recipient for the transaction (it could be set to None or a placeholder if not applicable)
#                 recipient = None  # Replace with actual recipient if available
                
#                 # Add the transaction to the blockchain
#                 blockchain.add_transaction(transaction, recipient, price, crop_id)

#                 # Create a new block to store the transaction
#                 blockchain.mine_block()

#                 messages.success(request, f"Crop '{crop_name}' listed successfully and added to the blockchain!")
#             except ValueError:
#                 messages.error(request, "Invalid quantity or price. Please enter numeric values.")
#         else:
#             messages.error(request, "All fields are required.")

#         return redirect('list_crops')

#     # Fetching all crops to display
#     crops = Crop.objects.all()
#     return render(request, 'list_crops.html', {'crops': crops})

@login_required
def list_crops(request):
    if request.user.role=='CUSTOMER':
        return render(request, 'not_allowed.html')
    
    if request.method == 'POST':
        crop_name = request.POST.get('name')
        quantity_str = request.POST.get('quantity')
        price_str = request.POST.get('price')

        if crop_name and quantity_str and price_str:
            try:
                quantity = float(quantity_str)
                price = float(price_str)

                crop = Crop.objects.create(
                    name=crop_name,
                    quantity=quantity,
                    price=price,
                    current_owner=request.user,
                    current_stage=f'Listed by {request.user.role}'
                )
                crop.save()

                # Prepare transaction details
                sender = request.user.username  # or user ID if needed
                recipient = None  # Depending on your application, this could be an actual recipient
                crop_id = crop.id

                # Add the transaction to the blockchain
                blockchain.add_transaction(sender, recipient, price, crop_id)

                # Mine a new block
                blockchain.mine_block()  # Call the mine_block method

                messages.success(request, f"Crop '{crop_name}' listed successfully and added to the blockchain!")
            except ValueError:
                messages.error(request, "Invalid quantity or price. Please enter numeric values.")
        else:
            messages.error(request, "All fields are required.")

        return redirect('list_crops')

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
def buy_crops(request, crop_id):
    # Get the crop based on crop_id
    if request.user.role=='FARMER':
        return render(request, 'not_allowed.html')
    
    crop = get_object_or_404(Crop, id=crop_id)

    if request.method == 'POST':
        # Handle the purchase logic
        quantity_to_buy = int(request.POST.get('quantity', 0))
        if quantity_to_buy <= 0 or quantity_to_buy > crop.quantity:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        # Add the transaction to the blockchain
        blockchain.add_transaction(
            sender=crop.current_owner.username,
            recipient=request.user.username,
            amount=crop.price * quantity_to_buy,
            crop_id=crop_id
        )

        # Mine a new block to confirm the transaction
        mined_block = blockchain.mine_block()

        # Create a transaction entry in the database
        transaction = Transaction.objects.create(
            seller=crop.current_owner,
            buyer=request.user,  # Assuming the user is logged in
            crop=crop,
            quantity=quantity_to_buy,
            price=crop.price,
            transaction_hash=mined_block.hash  # Use the block hash
        )

        # Create a PurchasedCrop entry
        purchased_crop = PurchasedCrop.objects.create(
            seller=crop.current_owner,
            buyer=request.user,
            crop=crop,
            quantity=quantity_to_buy,
            price=crop.price,
            transaction_hash=mined_block.hash  # Use the same hash for tracing
        )

        # Update the crop's quantity
        crop.quantity -= quantity_to_buy
        if crop.quantity == 0:
            crop.status = 'sold'
        crop.save()

        return render(request, 'purchase_success.html', {
            'transaction_id': transaction.id,
            'purchased_crop_id': purchased_crop.id
        })
    
    elif request.method == 'GET':
        # Optionally return crop details or a form for purchase
        return render(request, 'buy_crop.html', {
            'crop': crop
        })
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@login_required
def purchased_crops(request):
    # Example query, adjust as needed
    purchased_crops = PurchasedCrop.objects.filter(buyer=request.user)
    return render(request, 'purchased_crops.html', {'purchased_crops': purchased_crops})

@login_required
def trace_crops(request):
    # Get the crops purchased by the logged-in user
    purchased_crops = PurchasedCrop.objects.filter(buyer=request.user)

    # Add traceability information for each purchased crop
    crops_with_traceability = []
    for purchased_crop in purchased_crops:
        crop_id = purchased_crop.crop.id

        # Get the traceability information from the blockchain
        traceability_info = blockchain.trace_crop(crop_id)

        # Get the list of transactions related to this crop
        transactions = Transaction.objects.filter(crop_id=crop_id)

        # Append the crop data along with traceability and transaction information
        crops_with_traceability.append({
            'purchased_crop': purchased_crop,
            'traceability_info': traceability_info,
            'transactions': transactions,
        })

    # Pass the crops with traceability data to the template
    return render(request, 'trace_crop.html', {'crops_with_traceability': crops_with_traceability})

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
    logout(request)  # This will log out the user
    return redirect('dashboard')   # Redirect to a success page

# def logout_success(request):
#     return redirect('dashboard')

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


def view_blockchain(request):
    blockchain_data = blockchain.get_blockchain_data()  # Get blockchain data
    return render(request, 'view_blockchain.html', {'blockchain_data': blockchain_data})