from django.urls import path
from shop.views import (
    ProductList,
    ProductDetail,
    CategoryList,
    CategoryDetail,
    ProductImageList,
    ProductImageDetail,
    ProductSearchView
)


urlpatterns = [
    path('products/', ProductList.as_view(), name='products'),
    path('products/<int:id>/', ProductDetail.as_view(), name='product-detail'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('categories/<int:id>/',
         CategoryDetail.as_view(), name='category-detail'),
    path('images/', ProductImageList.as_view(), name='images'),
    path('images/<int:id>/',
         ProductImageDetail.as_view(), name='image-detail'),
    path('search/', ProductSearchView.as_view(), name='search'),
]
