from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from profile.models import Customer, Seller, Order, OrderItem, Cart, CartItem
from profile.permission import IsOwnerOrAdmin, IsOwner
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
                        "user": user.id,
                        "address": request.data.get("address")}
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
                    data={"user": user.id,
                          "address": request.data.get("address")}
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

        return Response(user_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def save_user_cart(self, serializer):
        return serializer.save(customer=self.request.user)


class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    CartDetail view only authenticated customer of the cart can
    access/mofify their cart
    get_queryset method filters the cart based on the
    authenticated user
    """

    permission_classes = [IsOwner]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)


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
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        cart_id = self.kwargs.get("cart_id")
        return CartItem.objects.filter(
            cart__id=cart_id, cart__customer=self.request.user
        )

    def add_product_in_cart(self, serializer):
        cartlist = CartList()
        cartlist.save_user_cart()  # TODO we need to test it
        cart_id = self.kwargs.get("cart_id")
        cart = Cart.objects.get(id=cart_id)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        if product.stock < quantity:
            raise serializers.ValidationError(
                {"message": "Product out of stock"})
        else:
            product.stock -= cart.quantity
            product.save()


class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    CartItemDetail view only authenticated customer of the cart can
    access/mofify their cart or superuser get_queryset method filters
    the cart based on the authenticated user, cart id and item id
    """

    # TODO remove access of OWNER after testing
    permission_classes = [IsOwnerOrAdmin]
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
            # TODO CHECK WITH A TEST IF THE INSTANCE IS SAVED
            instance.save()
            serialaizer = self.get_serializer(instance)
            return Response(serialaizer.data, status=status.HTTP_200_OK)
        return self.destroy(request, *args, **kwargs)

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
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def create_order(self, serializer):
        customer = self.request.user
        cart = Cart.objects.get(customer=customer)

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items:
            raise serializers.ValidationError({"message": "Cart is empty"})

        order = serializer.save(customer=customer)

        # TODO we need to change the Order and Cart
        # to have the price from product
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                shipping_address=customer.address,
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
    permission_classes = [IsOwnerOrAdmin]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

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
            cart_item = CartItem.objects.get(cart=cart,
                                             id=item["cart_item_id"])
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                shipping_address=self.choose_address(request, *args, **kwargs),
            )
            cart_item.delete()

        for item_id in remove_items:
            order_item = OrderItem.objects.get(order=order, id=item_id)
            order_item.delete()

        return Response(self.get_serializer(order).data,
                        status=status.HTTP_200_OK)


class SellerFilterView(generics.ListAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SellerFilter
