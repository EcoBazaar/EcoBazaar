from django.shortcuts import render
from shop.models import Product, Category, ProductImage
from shop.serializer import (
    ProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
)
from rest_framework import generics
from rest_framework import permissions


## ProductList and ProductDetail views created


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


## CategoryList and CategoryDetail views created


class CategoryList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


## ProductImageList and ProductImageDetail views created


class ProductImageList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductImageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
