from user.models import Seller
from user.serializers import CustomerSerializer, SellerSerializer
from user.serializers import UserSerializer

from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response, status
from rest_framework.views import APIView


# SellerList

class SellerList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


# SellerDetail

class SellerDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


# RegisterView

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
