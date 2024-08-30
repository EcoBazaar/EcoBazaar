from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from django.core.validators import RegexValidator


class Address(models.Model):
    street = models.CharField(max_length=250)
    postal_code = models.CharField(
        max_length=10,  # Set the max length as per your requirement
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}(?:-[0-9]{4})?$',
                message="Enter a valid postal code. Format: '12345' or '12345-6789'."
            ),
        ],
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=(
                    "Phone number must be entered in the format: '+999999999'."
                    " Up to 15 digits allowed."
                ),
            ),
        ],
    )
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}: {self.phone_number}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="customer_address",
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="seller_address",
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username


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
        if self.customer.user.first_name and self.customer.user.last_name:
            return f"Order {self.id} by {self.customer.user.first_name} \
                {self.customer.user.last_name}"

        return f"Order {self.id} by {self.customer.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
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
        if self.customer.user.first_name and self.customer.user.last_name:
            return f"Cart of {self.customer.user.first_name} \
                {self.customer.user.last_name}"
        return f"Cart of {self.customer.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,
                             on_delete=models.CASCADE,
                             related_name="cart_items")
    product = models.ForeignKey(
        "shop.Product", on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart"
