from django.contrib import admin

# Register your models here.

from .models import Address, Customer, Seller, Order, OrderItem

admin.site.register(Address)
admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Order)
admin.site.register(OrderItem)
