from django.db import models
from django.conf import settings 
from django.contrib.auth.models import AbstractUser
import hashlib
import json
from time import time

# Create your models here.

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('DISTRIBUTOR', 'Distributor'),
        ('CONSUMER', 'Consumer'),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    
class Crop(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()
    price = models.FloatField()
    current_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_crops')
    status = models.CharField(max_length=20, choices=[('listed', 'Listed'), ('sold', 'Sold')])
    current_stage = models.CharField(max_length=100, default='Listed by Farmer')
    transaction_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.quantity} kg - {self.current_stage}"


    
# class Crop(models.Model):
#     name = models.CharField(max_length=100)
#     quantity = models.FloatField()
#     price = models.FloatField()
#     current_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     current_stage = models.CharField(max_length=50, default="Listed by Farmer")

#     def __str__(self):
#         return f"{self.name} - {self.quantity} kg - {self.current_stage}"

# class Transaction(models.Model):
#     buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer')
#     seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller')
#     crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
#     quantity = models.FloatField()
#     price = models.FloatField()
#     transaction_hash = models.CharField(max_length=255) 
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Transaction: {self.seller} -> {self.buyer} | {self.crop.name}"


class Transaction(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_transactions', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchased_transactions', on_delete=models.CASCADE)  # Correct field name
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Block(models.Model):
    index = models.IntegerField(null=True)
    previous_hash = models.CharField(max_length=64)
    timestamp = models.FloatField(default=time)
    transactions = models.JSONField(default=list)  # Stores transactions as a JSON list
    proof = models.IntegerField()

    def __str__(self):
        return f"Block {self.index}"

    @classmethod
    def create_block(cls, index, previous_hash, transactions, proof):
        """Creates a new block and saves it to the database."""
        block = cls(
            index=index,
            previous_hash=previous_hash,
            timestamp=time.time(), 
            transactions=json.dumps(transactions),  # Convert transactions to JSON string for storage
            proof=proof
        )
        block.save()
        return block

    @classmethod
    def calculate_hash(cls, block):
        """Calculates the hash of a block."""
        block_string = json.dumps(block.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# class Block(models.Model):

class PurchasedCrop(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_crops', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='purchased_crops', on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchased: {self.crop.name} by {self.buyer.username} from {self.seller.username} | Quantity: {self.quantity} | Price: {self.price}"