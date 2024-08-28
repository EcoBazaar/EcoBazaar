from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

# Create your models here.


class Address(models.Model):
    address = models.CharField(max_length=250)
    postal_code = models.PositiveIntegerField()
    phone_number = models.PositiveBigIntegerField()
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}: {self.phone_number}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="customer_address", blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="seller_address", blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="customer"
    )
    product = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipping_address",
    )

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.first_name} \
    {self.customer.user.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(
        "shop.Product", on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.customer.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        "shop.Product", on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart"
