from shop.models import Product, Category, ProductImage
from shop.serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
)
from rest_framework import generics, filters
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response


class ProductList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response(
                {"message": "You must login to create a product"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.create(request, *args, **kwargs)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        if not request.superuser.is_authenticated:
            return Response(
                {"message": "You must login as a admin to create a category"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.create(request, *args, **kwargs)


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductImageList(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response(
                {"message": "You need to login to create a product image"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.create(request, *args, **kwargs)


class ProductImageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    # Adjust fields as necessary
    search_fields = ['name', 'description', 'category__name']
