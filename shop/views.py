import cloudinary.uploader
from shop.models import Product, Category, ProductImage
from shop.serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
)
from profile.serializers import (
    SellerProductSerializer
)
from rest_framework import generics, filters
from django.views.generic import ListView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

# for demo
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from profile.models import Cart, Seller
import django_filters

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter


class ProductList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response(
                {"message": "You must login to create a product"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.create(request, *args, **kwargs)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
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
        permissions.IsAdminUser,
    ]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductImageList(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response(
                {"message": "You need to login to create a product image"},
                status=status.HTTP_403_FORBIDDEN,
            )

        file = request.FILES.get('image')

        if file:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result.get('url')

            data = {
                'product': request.data.get('product'),
                'image_url': image_url
            }

            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProductImageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser,
    ]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "category__name"]


class SellerProductsAPIView(generics.RetrieveAPIView):
    permission_classes = []
    queryset = Seller.objects.all()
    serializer_class = SellerProductSerializer
    lookup_field = 'user__username'


# create demo views:
class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()
        filter = ProductFilter(self.request.GET, queryset=queryset)
        return filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ProductFilter(
            self.request.GET, queryset=self.get_queryset()
        )
        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart.products.add(product)
        # Redirect to the cart detail view
        return redirect('cart-detail')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the seller's address and add it to the context
        context['seller'] = self.object.seller
        context['address'] = self.object.seller.address
        return context


class SellerProductListView(ListView):
    model = Product
    template_name = 'shop/seller_product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Fetch the seller based on the username in the URL
        self.seller = get_object_or_404(
            Seller, user__username=self.kwargs['username']
        )
        # Filter products that belong to this seller
        return Product.objects.filter(seller=self.seller)

    def get_context_data(self, **kwargs):
        # Pass additional seller and address information to the template
        context = super().get_context_data(**kwargs)
        context['seller'] = self.seller
        context['address'] = self.seller.address
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'shop/category_list.html'
    context_object_name = 'categories'

# View for Category Detail


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'shop/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        # Add the list of products in the category to the context
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.category.all()
        return context


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte', label='Min Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte', label='Max Price'
    )
    city = django_filters.CharFilter(
        field_name='seller__address__city',
        lookup_expr='icontains',
        label='City'
    )

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'city']


class ProductSearchView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset
