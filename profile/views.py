from rest_framework.response import Response, status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, serializers, permissions

from profile.permission import IsOwnerOrAdmin
from profile.models import (
    Customer, 
    Seller, 
    Order, 
    OrderItem, 
    Cart, 
    CartItem
    )

from profile.permission import IsOwnerOrAdmin, IsOwner
from profile.models import Customer, Seller, Order, OrderItem, Cart, CartItem
from profile.serializers import (
    CustomerSerializer,
    SellerSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    AddressSeriaizer,
    UserSerializer,
    SellerUsernameSerializer,
)


class CustomerCreate(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class SellerList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


class SellerDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Seller.objects.all()

    def get_serializer_class(self):
        seller = self.get_object()

        # Check if the requesting user is the seller or an admin
        if self.request.user == seller.user or self.request.user.is_staff:
            return SellerSerializer  # Full profile for seller and admin
        else:
            return SellerUsernameSerializer  # Limited profile for others


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        # Serialize the User data
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            # Save the User instance
            user = user_serializer.save()

            # Check the role and create the appropriate profile
            if request.data.get("role") == "seller":
                seller_serializer = SellerSerializer(
                    data={"user": user.id, "address": request.data.get("address")}
                )

                if seller_serializer.is_valid():
                    seller_serializer.save()
                else:
                    user.delete()
                    return Response(
                        seller_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            else:  # Default to customer if role is not 'seller'
                customer_serializer = CustomerSerializer(
                    data={"user": user.id, "address": request.data.get("address")}
                )

                if customer_serializer.is_valid():
                    customer_serializer.save()
                else:
                    user.delete()
                    return Response(
                        customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )

        # Return errors if UserSerializer is invalid
        return Response(user_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
    


class LoginView(APIView):
    permission_classes = []
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartList(generics.ListCreateAPIView):
    """CartList and CartDetail views only authenticated users can
    access/mofify their cart or superuser
    get_queryset method filters the cart based on the authenticated user
    save_user_cart method saves the cart with the authenticated user"""

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]  # TODO remove access of OWNER after testing

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def save_user_cart(self, serializer):
        return serializer.save(customer=self.request.user)


class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    """CartDetail view only authenticated customer of the cart can
      access/mofify their cart
    get_queryset method filters the cart based on the
      authenticated user"""

    permission_classes = [IsOwner]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)


class CartItemList(generics.ListCreateAPIView):
    """CartItemList view only authenticated customer of the cart
      can access/mofify their cart or superuser
    product_in_cart method checks if the product is in stock and
      adds it to the cart
    get_queryset method filters the cart based on the authenticated
    user and cart id"""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        cart_id = self.kwargs.get("cart_id")
        return CartItem.objects.filter(
            cart__id=cart_id, cart__customer=self.request.user
        )

    def add_product_in_cart(self, serializer):
        cart_id = self.kwargs.get("cart_id")
        cart = Cart.objects.get(id=cart_id)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        if product.stock < quantity:
            raise serializers.ValidationError({"message": "Product out of stock"})
        else:
            product.stock -= cart.quantity
            product.save()


class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """CartItemDetail view only authenticated customer of the cart can
    access/mofify
      their cart or superuser
    get_queryset method filters the cart based on the authenticated user,
    cart id and item id
    """

    permission_classes = [IsOwnerOrAdmin]  # TODO remove access of OWNER after testing
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart_id = self.kwargs.get("cart_id")
        item_id = self.kwargs.get("pk")
        return CartItem.objects.filter(
            cart__id=cart_id, cart__customer=self.request.user, pk=item_id
        )

    def update(self, request, *args, **kwargs):
        """
        method to update the quantity of the product in the cart"""
        instance = self.get_object()
        quantity = request.data.get("quantity", None)

        if quantity >= 1:
            instance.quantity = quantity
            instance.product.stock -= instance.quantity
            instance.product.save()
            instance.save()  # TODO CHECK WITH A TEST IF THE INSTANCE IS SAVED
            serialaizer = self.get_serializer(instance)
            return Response(serialaizer.data, status=status.HTTP_200_OK)
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """method to delete the product from the cart and add the quantity back
        to the stock"""
        instance = self.get_object()
        instance.product.stock += instance.quantity
        instance.product.save()
        return super().destroy(request, *args, **kwargs)
