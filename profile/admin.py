from django.contrib import admin
from .models import Address, Customer, Seller, Order, OrderItem


class SellerAdmin(admin.ModelAdmin):
    list_display = ("user",)
    
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user",)
    
    
admin.site.register(Address)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)