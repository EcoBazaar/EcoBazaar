from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Product, Category
from profile.models import Seller


class ProductAPITest(APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="adminpass"
        )
        self.regular_user = User.objects.create_user(
            username="user", password="userpass"
        )
        self.category = Category.objects.create(
            name="Electronics", slug="electronics")
        self.seller = Seller.objects.create(user=self.regular_user)
        self.product = Product.objects.create(
            name="Test Product",
            price=99.99,
            stock=10,
            seller=self.seller,
            category=self.category,
        )

    def test_list_products(self):
        url = reverse("products")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("products")
        data = {
            "name": "New Product",
            "price": 49.99,
            "stock": 5,
            "seller": self.seller.id,
            "category_id": self.category.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(
            Product.objects.get(id=response.data["id"]).name, "New Product"
        )

    def test_create_product_as_regular_user(self):
        url = reverse("products")
        data = {
            "name": "New Product",
            "price": 49.99,
            "stock": 5,
            "seller": self.seller.id,
            "category": self.category.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_retrieve_product_as_authenticated_user(self):
        self.client.force_authenticate(user=self.superuser)
        self.client.force_authenticate(
            user=self.regular_user)

        url = reverse("product-detail", args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Product")
        self.assertEqual(float(response.data["price"]), 99.99)

    def test_update_product_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("product-detail", args=[self.product.id])
        data = {
            "name": "Updated Product Name",
            "price": 59.99,
            "stock": 15,
            "seller": self.seller.id,
            "category_id": self.category.id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product Name")

    def test_delete_product_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("product-detail", args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_product_by_name(self):
        url = reverse("search")
        response = self.client.get(url, {"search": "Test Product"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertGreater(len(response.data), 0)
