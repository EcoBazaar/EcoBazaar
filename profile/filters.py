import django_filters as filters
from profile.models import Seller
from django_filters.rest_framework import FilterSet


class SellerFilter(FilterSet):
    city = filters.CharFilter(
        field_name="address_city",
        lookup_expr="icontains")

    class Meta:
        model = Seller
        fields = ["city"]
