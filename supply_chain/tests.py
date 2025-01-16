from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Crop, Transaction, Blockchain, UserSpecificCrop

User = get_user_model()


class SupplyChainTests(TestCase):
    def setUp(self):
        # Create test users
        self.farmer = User.objects.create_user(username='farmer', password='password', role='FARMER', balance=1000)
        self.distributor = User.objects.create_user(username='distributor', password='password', role='DISTRIBUTOR', balance=500)
        self.consumer = User.objects.create_user(username='consumer', password='password', role='CONSUMER', balance=300)

        # Create a test crop
        self.crop = Crop.objects.create(
            name="Wheat",
            quantity=100,
            price=50.0,
            current_owner=self.farmer,
            current_stage="Listed by Farmer",
            visibility="public"
        )

        # Initialize blockchain
        self.blockchain = Blockchain()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'password'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_dashboard_farmer(self):
        self.client.login(username='farmer', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'farmer_dashboard.html')

    def test_dashboard_distributor(self):
        self.client.login(username='distributor', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'distributor_dashboard.html')

    def test_dashboard_consumer(self):
        self.client.login(username='consumer', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consumer_dashboard.html')

    def test_list_crops(self):
        self.client.login(username='farmer', password='password')
        response = self.client.get(reverse('list_crops'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_crops.html')

    def test_buy_crops_successful(self):
        self.client.login(username='distributor', password='password')
        response = self.client.post(reverse('buy_crops', args=[self.crop.id]), {
            'quantity': 10
        })
        self.assertEqual(response.status_code, 200)
        self.crop.refresh_from_db()
        self.assertEqual(self.crop.quantity, 90)

    def test_buy_crops_insufficient_balance(self):
        self.client.login(username='consumer', password='password')  # Consumer with insufficient balance
        response = self.client.post(reverse('buy_crops', args=[self.crop.id]), {
            'quantity': 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Insufficient balance')

    def test_buy_crops_invalid_quantity(self):
        self.client.login(username='distributor', password='password')
        response = self.client.post(reverse('buy_crops', args=[self.crop.id]), {
            'quantity': 200  # More than available quantity
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid quantity')

