

# supply_chain/admin.py
from django.contrib import admin
from .models import CustomUser, Crop, Transaction

admin.site.register(CustomUser)
admin.site.register(Crop)
admin.site.register(Transaction)

