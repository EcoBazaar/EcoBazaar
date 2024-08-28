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


from profile.permission import IsOwnerOrAdmin
from profile.models import (
    Customer, 
    Seller, 
    Order, 
    OrderItem, 
    Cart, 
    CartItem
    )
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
            if request.data.get('role') == 'seller':
                seller_serializer = SellerSerializer(
                    data={"user": user.id,
                          "address": request.data.get('address')})

                if seller_serializer.is_valid():
                    seller_serializer.save()
                else:
                    user.delete()
                    return Response(seller_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

            else:  # Default to customer if role is not 'seller'
                customer_serializer = CustomerSerializer(
                    data={"user": user.id,
                          "address": request.data.get('address')})

                if customer_serializer.is_valid():
                    customer_serializer.save()
                else:
                    user.delete()
                    return Response(customer_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "User created successfully"},
                            status=status.HTTP_201_CREATED)

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
