from rest_framework import serializers
from .models import Category, Product, ProductImage


<<<<<<< HEAD
# Serializer for Category
=======
>>>>>>> origin/main
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(
<<<<<<< HEAD
        many=True, read_only=True
    )  # To include related images
    category = CategorySerializer(
        read_only=True
    )  # To display the category as a nested object
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category"
    )  # To assign a category
=======
        many=True, read_only=True)  # To include related images
    # To display the category as a nested object
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category')
>>>>>>> origin/main

    class Meta:
        model = Product
        fields = "__all__"
