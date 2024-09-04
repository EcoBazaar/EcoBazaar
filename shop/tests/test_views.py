from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from shop.models import Product, Category, ProductImage
from shop.serializers import ProductSerializer, CategorySerializer, ProductImageSerializer
import cloudinary.uploader
from unittest.mock import patch, MagicMock


class ProductListTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password123')
        self.client.login(username='admin', password='password123')
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.url = reverse('products')
        
    def test_get_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_as_superuser(self):
        data = {
            'name': 'Smartphone',
            'price': '299.99',
            'description': 'Latest model smartphone',
            'stock': 10,
            'category': self.category.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        
    def test_create_product_as_non_superuser(self):
        self.client.logout()
        self.user = User.objects.create_user(username='user', password='password123')
        self.client.login(username='user', password='password123')
        data = {
            'name': 'Smartphone',
            'price': '299.99',
            'description': 'Latest model smartphone',
            'stock': 10,
            'category': self.category.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class ProductDetailTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_superuser(username='admin', password='password123')
#         self.client.login(username='admin', password='password123')
#         self.category = Category.objects.create(name="Electronics", slug="electronics")
#         self.product = Product.objects.create(
#             name="Smartphone",
#             price="299.99",
#             description="Latest model smartphone",
#             stock=10,
#             category=self.category,
#             seller=self.user
#         )
#         self.url = reverse('product-detail', kwargs={'id': self.product.id})

#     def test_get_product_detail(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['name'], 'Smartphone')

#     def test_update_product(self):
#         data = {'price': '250.00'}
#         response = self.client.put(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.product.refresh_from_db()
#         self.assertEqual(self.product.price, '250.00')

#     def test_delete_product(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Product.objects.count(), 0)



# class CategoryListTests(APITestCase):
    
#     def setUp(self):
#         self.user = User.objects.create_superuser(username='admin', password='password123')
#         self.client.login(username='admin', password='password123')
#         self.url = reverse('categories')
        
#     def test_get_categories(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_create_category_as_superuser(self):
#         data = {
#             'name': 'Books',
#             'slug': 'books'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Category.objects.count(), 1)
        
#     def test_create_category_as_non_superuser(self):
#         self.client.logout()
#         self.user = User.objects.create_user(username='user', password='password123')
#         self.client.login(username='user', password='password123')
#         data = {
#             'name': 'Books',
#             'slug': 'books'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# class CategoryDetailTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_superuser(username='admin', password='password123')
#         self.client.login(username='admin', password='password123')
#         self.category = Category.objects.create(name="Electronics", slug="electronics")
#         self.url = reverse('category-detail', kwargs={'category_slug': self.category.slug})

#     def test_get_category_detail(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['name'], 'Electronics')

#     def test_update_category(self):
#         data = {'name': 'Tech'}
#         response = self.client.put(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.category.refresh_from_db()
#         self.assertEqual(self.category.name, 'Tech')

#     def test_delete_category(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Category.objects.count(), 0)


# class ProductImageListTests(APITestCase):
    
#     def setUp(self):
#         self.user = User.objects.create_superuser(username='admin', password='password123')
#         self.client.login(username='admin', password='password123')
#         self.product = Product.objects.create(
#             name="Smartphone",
#             price="299.99",
#             description="Latest model smartphone",
#             stock=10,
#             category=Category.objects.create(name="Electronics", slug="electronics"),
#             seller=self.user
#         )
#         self.url = reverse('images')
        
#     @patch('shop.views.cloudinary.uploader.upload')
#     def test_upload_image_as_superuser(self, mock_upload):
#         mock_upload.return_value = {'url': 'http://example.com/image.jpg'}
#         data = {
#             'product': self.product.id,
#             'image': MagicMock()  # Mock the file upload
#         }
#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(ProductImage.objects.count(), 1)
        
#     def test_upload_image_as_non_superuser(self):
#         self.client.logout()
#         self.user = User.objects.create_user(username='user', password='password123')
#         self.client.login(username='user', password='password123')
#         data = {
#             'product': self.product.id,
#             'image': MagicMock()  # Mock the file upload
#         }
#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class ProductImageDetailTests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_superuser(username='admin', password='password123')
#         self.client.login(username='admin', password='password123')
#         self.product = Product.objects.create(
#             name="Smartphone",
#             price="299.99",
#             description="Latest model smartphone",
#             stock=10,
#             category=Category.objects.create(name="Electronics", slug="electronics"),
#             seller=self.user
#         )
#         self.product_image = ProductImage.objects.create(
#             product=self.product,
#             image_url='http://example.com/image.jpg'
#         )
#         self.url = reverse('image-detail', kwargs={'id': self.product_image.id})

   
