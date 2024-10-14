from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('distributor', 'Distributor'),
        ('vendor', 'Vendor'),
        ('wholesaler', 'Wholesaler'),
        ('retailer', 'Retailer'),
        ('consumer', 'Consumer'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"

class Crop(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_id = models.CharField(max_length=50, unique=True)
    seller = models.ForeignKey(User, related_name='crops', on_delete=models.CASCADE)  # Link to the seller

    def __str__(self):
        return self.name

class Transaction(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buyer', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])

    def __str__(self):
        return f"{self.buyer} bought {self.quantity} kg of {self.crop.name} from {self.seller} for ₹{self.total_price} on {self.date.strftime('%Y-%m-%d')}"
