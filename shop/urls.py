from django.urls import path
from shop.views import (
    ProductList,
    ProductDetail,
    CategoryList,
    CategoryDetail,
    ProductImageList,
    ProductImageDetail,
    ProductSearchView,

    # view for demo
    ProductListView,
    ProductDetailView,
    AddToCartView,
    SellerProductListView,
    CategoryListView,
    CategoryDetailView,
    ProductSearchDemoView,
)


urlpatterns = [
    path("api/products/", ProductList.as_view(), name="products"),
    path("api/products/<int:pk>/", ProductDetail.as_view(),
         name="product-detail"),
    path("api/categories/", CategoryList.as_view(), name="categories"),
    path("api/categories/<slug:category_slug>/", CategoryDetail.as_view(),
         name="category-detail"),
    path("api/images/", ProductImageList.as_view(), name="images"),
    path("api/images/<int:pk>/", ProductImageDetail.as_view(),
         name="image-detail"),
    path("api/search/", ProductSearchView.as_view(), name="search"),

    # url for demo
    path('products/', ProductListView.as_view(), name='products-demo'),
    path('product/<int:pk>/', ProductDetailView.as_view(),
         name='product-detail-demo'),
    path('product/<int:product_id>/add-to-cart/',
         AddToCartView.as_view(), name='add-to-cart-demo'),
    path('seller/<str:username>/products/',
         SellerProductListView.as_view(), name='seller-products-demo'),
    path('categories/', CategoryListView.as_view(), name='category-list-demo'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(),
         name='category-detail-demo'),
    path('search/', ProductSearchDemoView.as_view(), name='search-demo'),
]
