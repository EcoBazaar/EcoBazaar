from django_filters import restframework as filters
from profile.models import Seller


class SellerFilter(filters.FilterSet):
    city = filters.CharFilter(
        field_name="address_city", 
        lookup_expr="icontains")

    class Meta:
        model = Seller
        fields = ["city"]
