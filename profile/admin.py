from django.contrib import admin
from .models import Address, Customer, Seller, Order, OrderItem, Cart, CartItem


class SellerAdmin(admin.ModelAdmin):
    list_display = ("user",)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user",)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'postal_code', 'phone_number')
    search_fields = ('street', 'city', 'postal_code')


admin.site.register(Address, AddressAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(Cart)
