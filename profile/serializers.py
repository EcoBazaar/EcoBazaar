from rest_framework import serializers
from django.contrib.auth.models import User

from shop.models import Product
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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        write_only=True
    )
    address_details = AddressSerializer(read_only=True, source="address")
    products = ProductSerializer(
        many=True, read_only=True, source="user.product_set")

    class Meta:
        model = Customer
        fields = ["user", "address", "products", "address_details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = False

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user = instance.user
        if user.first_name and user.last_name:
            representation["full_name"] = f"{user.first_name} {user.last_name}"

        representation["username"] = user.username

        return representation


class SellerSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        write_only=True
    )
    address_details = AddressSerializer(read_only=True, source="address")
    products = ProductSerializer(
        many=True, read_only=True, source="user.product_set")

    class Meta:
        model = Seller
        fields = ["user", "address", "products", "address_details"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user = instance.user
        if user.first_name and user.last_name:
            representation["full_name"] = f"{user.first_name} {user.last_name}"

        representation["username"] = user.username

        return representation


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["order_items", "customer", "cart",
                  "created_at", "shipping_address"]
        read_only_fields = ["id", "customer", "order_items"]

    def create(self, validated_data):

        return Order.objects.create(**validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = CartItem
        fields = "__all__"

    def create(self, validated_data):
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        cart = validated_data.get('cart')

        # Ensure the product stock is sufficient
        if product.stock < quantity:
            raise serializers.ValidationError(
                {"message": "Product out of stock."}
            )

        # Create or update the CartItem
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                raise serializers.ValidationError(
                    {"message": "Product out of stock."}
                )
            cart_item.save()

        # Update the product stock
        product.stock -= quantity
        product.save()

        return cart_item


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


class SellerProductSerializer(serializers.ModelSerializer):
    products = ProductSerializer(
        many=True, read_only=True, source="user.product_set"
    )
    address = AddressSerializer(read_only=True, source="address")

    class Meta:
        model = Seller
        fields = ["user", "products", "address"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = instance.user
        # Optionally include the full name if available
        if user.first_name and user.last_name:
            representation["full_name"] = f"{user.first_name} {user.last_name}"
        representation["username"] = user.username
        return representation
