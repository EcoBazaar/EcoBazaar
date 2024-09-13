from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, serializers
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.edit import UpdateView

# for demo
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404

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
    SellerProductSerializer,
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
            return SellerProductSerializer  # Limited profile for others


class RegisterView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save()

            # Create default Customer profile for the user
            customer_serializer = CustomerSerializer(
                data={"user": user.id}
            )

            if customer_serializer.is_valid():
                customer_serializer.save()
                return Response(
                    {"message": "User created as a Customer successfully"},
                    status=status.HTTP_201_CREATED
                )
            else:
                user.delete()
                return Response(
                    customer_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
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

        if new_quantity == 0:
            instance.product.stock += current_quantity
            instance.product.save()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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


# Profile API View
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        customer = Customer.objects.filter(user=user).first()
        seller = Seller.objects.filter(user=user).first()

        if customer:
            user_data = CustomerSerializer(customer).data
        elif seller:
            user_data = SellerSerializer(seller).data
        else:
            return Response(
                {"error": "User is neither a customer nor a seller."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(user_data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        # Check if the user is already a seller
        if Seller.objects.filter(user=user).exists():
            return Response(
                {"error": "You are already a seller."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Upgrade user to seller
        customer = Customer.objects.filter(user=user).first()
        if not customer:
            return Response(
                {"error": "You need to be a customer to upgrade to seller."},
                status=status.HTTP_400_BAD_REQUEST
            )

        seller_data = {
            "user": user.id,
            # Assuming address is included in the request
            "address": request.data.get("address", ""),
        }
        seller_serializer = SellerSerializer(data=seller_data)

        if seller_serializer.is_valid():
            seller_serializer.save()
            return Response(
                {"message": "Successfully upgraded to Seller."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                seller_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UpgradeToSellerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is already a seller
        if Seller.objects.filter(user=user).exists():
            return Response(
                {"error": "User is already a seller."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a seller profile
        seller_serializer = SellerSerializer(
            data={
                "user": user.id,
                "address": request.data.get("address")
            }
        )

        if seller_serializer.is_valid():
            seller_serializer.save()
            return Response(
                {"message": "User upgraded to seller successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                seller_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

# demo views
# Register View


class RegisterDemoView(View):
    def get(self, request):
        return render(request, 'profile/register.html')

    def post(self, request):
        data = {
            "username": request.POST['username'],
            "email": request.POST['email'],
            "password": request.POST['password'],
            "first_name": request.POST['first_name'],
            "last_name": request.POST['last_name'],
        }
        user_serializer = UserSerializer(data=data)

        if user_serializer.is_valid():
            user = user_serializer.save()
            # Create a Customer profile for the newly registered user
            customer_serializer = CustomerSerializer(
                data={"user": user.id}
            )

            if customer_serializer.is_valid():
                customer_serializer.save()
                messages.success(
                    request, "Registration successful. Please log in.")
                # Redirect to login after successful registration
                return redirect('login-demo')
            else:
                user.delete()
                errors = customer_serializer.errors
                return render(
                    request, 'profile/register.html', {"errors": errors}
                )
        else:
            errors = user_serializer.errors
            return render(
                request, 'profile/register.html', {"errors": errors}
            )

# Login View


class LoginDemoView(View):
    def get(self, request):
        return render(request, 'profile/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(
            request, username=username, password=password
        )

        if user is not None:
            login(request, user)
            # Redirect to home or other page after login
            return redirect('products-demo')
        else:
            messages.error(request, "Invalid credentials")
            return render(request, 'profile/login.html')

# Logout View


class LogoutDemoView(View):
    def get(self, request):
        logout(request)
        return redirect('products-demo')  # Redirect to login after logout


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'profile/profile.html'
    fields = ['address']  # Fields you want to allow the user to update
    # Redirect after a successful update
    success_url = reverse_lazy('profile-view')

    def get_object(self, queryset=None):
        # Get the Customer object for the currently logged-in user
        return get_object_or_404(Customer, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UpgradeToSellerDemoView(View):
    def post(self, request, *args, **kwargs):
        user = request.user

        # Debug: print user information to verify request.user
        print(f"Upgrading user: {user}")

        if Seller.objects.filter(user=user).exists():
            messages.info(request, "You are already a seller.")
        else:
            try:
                Seller.objects.create(user=user)
                messages.success(
                    request,
                    "You have been upgraded to a seller."
                )
            except Exception as e:
                # Debug: Print the error in case of failure
                print(f"Error creating seller: {e}")
                messages.error(
                    request,
                    "There was an issue upgrading to a seller.\
                          Please try again."
                )

        return redirect('profile-view')


class ProductCreateView(CreateView):
    pass
