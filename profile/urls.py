from django.urls import path
from profile.views import (
    CustomerListCreateView,
    CustomerDetail,
    SellerList,
    SellerDetail,
    CartDetail,
    CartItemList,
    CartItemDetail,
    OrderList,
    OrderDetail,
    CartList,

)
urlpatterns = [
    path('customers/', CustomerListCreateView.as_view(), name='customers'),
    path('customer/<int:pk>/',
         CustomerDetail.as_view(), name='customer-detail'),
    path('sellers/', SellerList.as_view(), name='sellers'),
    path('seller/<int:pk>/', SellerDetail.as_view(), name='seller-detail'),
    path('customer/<int:customer_id>/cart/', CartList.as_view(), name='carts'),
    path('customer/<int:customer_id>/cart/<int:pk>/', CartDetail.as_view(), name='carts-detail'),
    path('customer/<int:customer_id>/cart-items/', CartItemList.as_view(), name='cart'), # TODO not test yet
    path('customer/<int:customer_id>/cart-item/<int:cart_id>/',
         CartItemDetail.as_view(), name='cart-detail'), # TODO not test yet
    path('customer/<int:customer_id>/order/<int:cart_id>/', OrderList.as_view(), name='order'),
    path('customer/<int:customer_id>/order/<int:cart_id>/<int:pk>/', # pk is item id
         OrderDetail.as_view(), name='order-detail'),     
]
