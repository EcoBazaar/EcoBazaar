from shop.models import Product
import django_filters as filters
from django_filters.rest_framework import FilterSet


class ProductFilter(FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["min_price", "max_price"]
