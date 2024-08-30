from django.urls import path
from profile.views import (
    CustomerCreate,
    CustomerDetail,
    SellerList,
    SellerDetail,
    CartDetail,
    CartItemList,
    CartItemDetail,
    OrderList,
    OrderDetail,

)
urlpatterns = [
    path('customers/', CustomerCreate.as_view(), name='customers'),
    path('customer/<int:id>/',
         CustomerDetail.as_view(), name='customer-detail'),
    path('sellers/', SellerList.as_view(), name='sellers'),
    path('seller/<int:id>/', SellerDetail.as_view(), name='seller-detail'),
    # path('carts/', CartList.as_view(), name='carts'),
    path('carts/<int:id>/', CartDetail.as_view(), name='carts-detail'),
    path('cart/<int:cart_id>/', CartItemList.as_view(), name='cart'),
    path('cart/<int:cart_id>/<int:pk>/',
         CartItemDetail.as_view(), name='cart-detail'),
    path('order/<int:cart_id>/', OrderList.as_view(), name='order'),
    path('order/<int:cart_id>/<int:pk>/',
         OrderDetail.as_view(), name='order-detail'),     
]
