# supply_chain/urls.py
from django.urls import path
from .views import (
    login_view,
    farmer_dashboard,
    distributor_dashboard,
    vendor_dashboard,
    wholesaler_dashboard,
    retailer_dashboard,
    consumer_dashboard,
    create_transaction_view,
    sell_crop_view,
    transaction_list_view,
    logout_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    
    # Role-based dashboards
    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('distributor/dashboard/', distributor_dashboard, name='distributor_dashboard'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('wholesaler/dashboard/', wholesaler_dashboard, name='wholesaler_dashboard'),
    path('retailer/dashboard/', retailer_dashboard, name='retailer_dashboard'),
    path('consumer/dashboard/', consumer_dashboard, name='consumer_dashboard'),
    
    # Transaction-related views
    path('create-transaction/', create_transaction_view, name='create_transaction'),
    path('sell-crop/', sell_crop_view, name='sell_crop'),
    path('transactions/', transaction_list_view, name='transaction_list'),
    
    # Logout view
    path('logout/', logout_view, name='logout'),
]