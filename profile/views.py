from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from profile.models import Customer, Seller, Order, OrderItem, Cart, CartItem
from profile.permission import (
    IsOwnerOrAdmin,
    IsCustomerOrAdminForRelatedObjects,
    IsSellerOrAdmin
    )
from profile.serializers import (
    CustomerSerializer,
    SellerSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    UserSerializer,
    SellerUsernameSerializer,
)

from django_filters.rest_framework import DjangoFilterBackend
from profile.filters import SellerFilter


class CustomerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOrAdmin]
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = SellerFilter


class SellerDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSellerOrAdmin]
    queryset = Seller.objects.all()

    def get_serializer_class(self):
        seller = self.get_object()

        if self.request.user == seller.user or self.request.user.is_staff:
            return SellerSerializer  # Full profile for seller and admin
        else:
            return SellerUsernameSerializer  # Limited profile for others


class RegisterView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save()

            # Check the role and create the appropriate profile
            if request.data.get("role") == "seller":
                seller_serializer = SellerSerializer(
                    data={
                        "user": user.id, "address": request.data.get("address")
                        }
                )

                if seller_serializer.is_valid():
                    seller_serializer.save()
                else:
                    user.delete()
                    return Response(
                        seller_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )

            else:  # Default to customer if role is not 'seller'
                customer_serializer = CustomerSerializer(
                    data={
                        "user": user.id, "address":
                        request.data.get("address")
                    }
                )

                if customer_serializer.is_valid():
                    customer_serializer.save()
                else:
                    user.delete()
                    return Response(
                        customer_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CartList(generics.ListCreateAPIView):
    """
    CartList and CartDetail views only authenticated users can
    access/mofify their cart or superuser
    get_queryset method filters the cart based on the authenticated user
    save_user_cart method saves the cart with the authenticated user
    """

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # TODO remove access of OWNER after testing
    permission_classes = [IsCustomerOrAdminForRelatedObjects]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.customer)

    def save_user_cart(self, serializer):
        return serializer.save(customer=self.request.user)


class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    CartDetail view only authenticated customer of the cart can
    access/mofify their cart
    get_queryset method filters the cart based on the
    authenticated user
    """

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsCustomerOrAdminForRelatedObjects]

    def get_queryset(self):
        # Ensure that only the cart belonging to
        # the authenticated user is accessed.
        return Cart.objects.filter(customer=self.request.user.customer)


class CartItemList(generics.ListCreateAPIView):
    """
    CartItemList view only authenticated customer of the cart
    can access/mofify their cart or superuser
    product_in_cart method checks if the product is in stock and
    adds it to the cart
    get_queryset method filters the cart based on the authenticated
    user and cart id
    """

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsCustomerOrAdminForRelatedObjects]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__customer=self.request.user.customer
        )

    def product_in_cart(self, serializer):
        cart = Cart.objects.get(customer=self.request.user.customer)
        serializer.save(cart=cart)


class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    CartItemDetail view only authenticated customer of the cart can
    access/mofify their cart or superuser get_queryset method filters
    the cart based on the authenticated user, cart id and item id
    """

    permission_classes = [IsCustomerOrAdminForRelatedObjects]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError("User is not authenticated")
        item_id = self.kwargs.get("pk")
        customer_id = self.kwargs.get("customer_id")
        queryset = CartItem.objects.filter(
            cart__customer__id=customer_id, pk=item_id
            )

        if not queryset.exists():
            raise serializers.ValidationError("Cart item not found")
        return queryset

    def update(self, request, *args, **kwargs):
        """
        method to update the quantity of the product in the cart"""
        instance = self.get_object()
        new_quantity = request.data.get("quantity", None)

        if new_quantity is None or new_quantity < 0:
            raise serializers.ValidationError(
                {"message": "Quantity must be greater than 0"}
            )

        current_quantity = instance.quantity

        if new_quantity > current_quantity:
            increase_amount = new_quantity - current_quantity
            if instance.product.stock >= increase_amount:
                instance.product.stock -= increase_amount
                instance.quantity = new_quantity
                instance.product.save()
            else:
                return Response(
                    {"message": "Product out of stock"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif new_quantity < current_quantity:
            decrease_amount = current_quantity - new_quantity
            instance.product.stock += decrease_amount
            instance.quantity = new_quantity
            instance.product.save()
        elif new_quantity == 0:
            instance.product.stock += current_quantity
            instance.quantity = new_quantity
            instance.product.save()
            return super().destroy(request, *args, **kwargs)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        method to delete the product from the cart and
        add the quantity back to the stock
        """
        instance = self.get_object()
        instance.product.stock += instance.quantity
        instance.product.save()
        return super().destroy(request, *args, **kwargs)


class OrderList(generics.ListCreateAPIView):
    """
    OrderList view only authenticated customer can access/mofify their order
    get_queryset method filters the order based on the authenticated user
    create_order method creates the order and adds the items
    from the cart to the order and deletes the cart items
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # TODO remove access of OWNER after testing
    permission_classes = [IsCustomerOrAdminForRelatedObjects]

    def create(self, request, *args, **kwargs):
        # Create the order for the authenticated user
        customer = request.user.customer
        cart = Cart.objects.get(customer=customer)

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items:
            raise serializers.ValidationError({"message": "Cart is empty"})

        # Use the serializer to create the order
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=customer)

        # Add cart items to order and delete them from the cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                cart_item=item,
                quantity=item.quantity
            )

        cart_items.delete()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    OrderDetail view only authenticated customer of the order can
    access/mofify their order get_queryset method filters the
    order based on the authenticated user and order id update_order
    method updates the order by adding or removing articles from the order
    """

    # TODO remove access of OWNER after testing
    permission_classes = [IsCustomerOrAdminForRelatedObjects]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer)

    def choose_address(self, request, *args, **kwargs):
        order = self.get_object()
        for address in request.user.address.all():
            if address.id == request.data.get("address_id"):
                order.shipping_address = address
                order.save()
                return Response(
                    self.get_serializer(order).data, status=status.HTTP_200_OK
                )

    def update_order(self, request, *args, **kwargs):
        order = self.get_object()

        add_items = request.data.get("add_items", None)
        remove_items = request.data.get("remove_items", None)

        cart = Cart.objects.get(customer=self.request.user)
        # Adding articles to the order
        for item in add_items:
            cart_item = CartItem.objects.get(
                cart=cart, id=item["cart_item_id"]
            )
            OrderItem.objects.create(
                order=order,
                cart_item=cart_item,
                quantity=cart_item.quantity,
                shipping_address=self.choose_address(request, *args, **kwargs),
            )
            cart_item.delete()

        for item_id in remove_items:
            order_item = OrderItem.objects.get(order=order, id=item_id)
            order_item.delete()

        return Response(
            self.get_serializer(order).data, status=status.HTTP_200_OK
        )
