from rest_framework import serializers
from django.contrib.auth.models import User

from shop.serializers import ProductSerializer
from .models import Address, Customer, Seller, Order, OrderItem, Cart, CartItem


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class AddressSeriaizer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"


class SellerUsernameSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True, source="seller")

    class Meta:
        model = Seller
        fields = ["user", "products"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["username"] = instance.user.username
        representation.pop("user", None)
        return representation
