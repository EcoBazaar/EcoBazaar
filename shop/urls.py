from django.urls import path
from shop.views import (
    ProductList,
    ProductDetail,
    CategoryList,
    CategoryDetail,
    ProductImageList,  # Handles listing and uploading product images
    ProductImageDetail,
    ProductSearchView,

    #view for demo
    ProductListView
)


urlpatterns = [
    path("api/products/", ProductList.as_view(), name="products"),
    path("api/products/<int:pk>/", ProductDetail.as_view(), name="product-detail"),
    path("api/categories/", CategoryList.as_view(), name="categories"),
    path("api/categories/<slug:category_slug>/", CategoryDetail.as_view(),
         name="category-detail"),
    path("api/images/", ProductImageList.as_view(), name="images"),
    path("api/images/<int:pk>/", ProductImageDetail.as_view(),
         name="image-detail"),
    path("api/search/", ProductSearchView.as_view(), name="search"),

    # url for demo
    path('products/', ProductListView.as_view(), name='product-list'),
]
