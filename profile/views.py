from rest_framework.response import Response, status
from rest_framework.views import APIView


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
    


## CartList and CartDetail views only authenticated users can access/mofify their cart or superuser
## get_queryset method filters the cart based on the authenticated user
## save_user_cart method saves the cart with the authenticated user
class CartList(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

    def save_user_cart(self, serializer):
        return serializer.save(customer=self.request.user)

## CartDetail view only authenticated customer of the cart can access/mofify their cart or superuser
## get_queryset method filters the cart based on the authenticated user
class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

## CartItemList view only authenticated customer of the cart can access/mofify their cart or superuser
## product_in_cart method checks if the product is in stock and adds it to the cart
## get_queryset method filters the cart based on the authenticated user and cart id
class CartItemList(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        cart_id = self.kwargs.get("cart_id")
        return CartItem.objects.filter(
            cart__id=cart_id, cart__customer=self.request.user
        )
    
    def product_in_cart(self, serializer):
        cart_id = self.kwargs.get("cart_id")
        cart = Cart.objects.get(id=cart_id)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        if product.stock < quantity:
            raise serializers.ValidationError({"message": "Product out of stock"})
        else:
            product.stock -= cart.quantity
            product.save()
    
## CartItemDetail view only authenticated customer of the cart can access/mofify their cart or superuser
## get_queryset method filters the cart based on the authenticated user, cart id and item id
##
class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart_id = self.kwargs.get("cart_id")
        item_id = self.kwargs.get("pk")
        return CartItem.objects.filter(
            cart__id=cart_id, cart__customer=self.request.user, pk=item_id
        )
## overriding the update method to update the quantity of the product in the cart
## if the quantity is less than 0, return a bad request
## if the quantity is 0, delete the product from the cart
## if the quantity is greater than 0, update the quantity of the product in the cart
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        quantity = request.data.get("quantity", None)

        if quantity is not None:
            if quantity < 0:
                return Response(
                    {"message": "Quantity cannot be less than 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif quantity == 0:
                return self.destroy(request, *args, **kwargs)
            else:
                instance.quantity = quantity
                instance.save()
                serialaizer = self.get_serializer(instance)
                return Response(
                    serialaizer.data, status=status.HTTP_200_OK
                )
        return super().update(request, *args, **kwargs)

## method to delete the product from the cart and add the quantity back to the stock
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.product.stock += instance.quantity
        instance.product.save()
        return super().destroy(request, *args, **kwargs)