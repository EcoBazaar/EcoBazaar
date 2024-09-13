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
    UpgradeToSellerView,

    # demo
    ProfileAPIView,
    ProfileView,
    ProductCreateView,

)

urlpatterns = [
    path(
        "api/customers/",
        CustomerListCreateView.as_view(), name="customers"),
    path(
        "api/customer/<int:pk>/",
        CustomerDetail.as_view(), name="customer-detail"),
    path("api/sellers/", SellerList.as_view(), name="sellers"),
    path("api/seller/<int:pk>/", SellerDetail.as_view(), name="seller-detail"),
    path("api/customer/<int:customer_id>/cart/",
         CartList.as_view(), name="carts"),
    path(
        "api/customer/<int:customer_id>/cart/<int:pk>/",
        CartDetail.as_view(),
        name="carts-detail",
    ),
    path(
        "api/customer/<int:customer_id>/cart-items/",
        CartItemList.as_view(), name="cart"),
    path(
        "api/customer/<int:customer_id>/cart-item/<int:pk>/",
        CartItemDetail.as_view(),
        name="cart-detail",
    ),
    path(
        "api/customer/<int:customer_id>/order/<int:cart_id>/",
        OrderList.as_view(),
        name="order",
    ),
    path(
        "api/customer/<int:customer_id>/order/<int:cart_id>/<int:pk>/",
        OrderDetail.as_view(),
        name="order-detail",
    ),

    path(
        'api/upgrade-to-seller/',
        UpgradeToSellerView.as_view(),
        name='upgrade-to-seller'
    ),

    path('api/profile/', ProfileAPIView.as_view(), name='profile-api'),

    # demo
    path('', ProfileView.as_view(), name='profile-view'),
    path('upgrade-to-seller/', UpgradeToSellerView.as_view(),
         name='upgrade-to-seller-demo'),
    path('add-product/', ProductCreateView.as_view(), name='add-product-demo'),
]
