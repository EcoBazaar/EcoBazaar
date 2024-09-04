from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Product, Category
from profile.models import Seller

class ProductAPITest(APITestCase):
    
    def setUp(self):
        #
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')  #create dummy user a superuser
        self.regular_user = User.objects.create_user(username='user', password='userpass')
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.seller = Seller.objects.create(user=self.regular_user)
        self.product = Product.objects.create(
            name='Test Product',
            price=99.99,
            stock=10,
            seller=self.seller,
            category=self.category 
        )

    # def test_list_products(self):               # OKAY
    #     url = reverse('products')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)



    def test_create_product_as_superuser(self):                # error #####
        self.client.login(username='admin', password='adminpass')
        url = reverse('products')
        data = {
            "name": "New Product",
            "price": 49.99,
            "stock": 5,
            "seller": self.seller.id,
            "category": self.category.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(id=response.data['id']).name, "New Product")



    # def test_create_product_as_regular_user(self):                # OKAY
    #     self.client.login(username='user', password='userpass')
    #     url = reverse('products')
    #     data = {
    #         "name": "New Product",
    #         "price": 49.99,
    #         "stock": 5,
    #         "seller": self.seller.id,
    #         "category": self.category.id,
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


                     
    # def test_retrieve_product_as_authenticated_user(self):       # OKAY
    #        # Log in as the admin user
    #     login_success = self.client.login(username='admin', password='adminpass')
    #     self.assertTrue(login_success, "Login failed")

    #     # Access the product detail endpoint
    #     url = reverse('product-detail', args=[self.product.id])
    #     response = self.client.get(url)

    #     # Print debug information
    #     print(f"Response status code: {response.status_code}")
    #     print(f"Response data: {response.data}")

    #     # Check the status code and response data
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['name'], 'Test Product')
    #     self.assertEqual(float(response.data['price']), 99.99)


    # def test_update_product_as_superuser(self):              # error
    #     self.client.login(username='admin', password='adminpass')
    #     url = reverse('product-detail', args=[self.product.id])
    #     data = {
    #         'name': 'Updated Product Name',
    #         'price': 59.99,
    #         'stock': 15,
    #         'seller': self.seller.id,
    #         'category': self.category.id
    #     }
    #     response = self.client.put(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.product.refresh_from_db()
    #     self.assertEqual(self.product.name, 'Updated Product Name')



    # def test_delete_product_as_superuser(self):              # error
    #     self.client.login(username='admin', password='adminpass')
    #     url = reverse('product-detail', args=[self.product.id])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_search_product_by_name(self):                   # error
    #     url = reverse('search')
    #     response = self.client.get(url, {'search': 'Test Product'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertGreater(len(response.data), 0)













# from rest_framework.test import APITestCase, APIClient
# from rest_framework import status
# from django.urls import reverse
# from shop.models import Category, Product, ProductImage
# from django.contrib.auth.models import User
# from profile.models import Seller

# class ProductAPITest(APITestCase):
    
#     def setUp(self):
#         self.category = Category.objects.create(name="Electronics")
#         self.user = User.objects.create(username="testseller", password="testpassword")
#         self.seller = Seller.objects.create(user=self.user)
#         self.product = Product.objects.create(
#             name='Test Product',
#             price=99.99,
#             stock=10,
#             seller=self.seller,
#             category=self.category 
#             )

#     # def test_get_product_list(self):
#     #     url = reverse('products')   # product-list seems to better naming
#     #     response = self.client.get(url)
#     #     self.assertEqual(response.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(len(response.data), 1)
    
#     def test_create_product(self):
#         url = reverse('product-detail')  # Adjust this to your URL pattern name
#         data = {
#             "name": "New Product",
#             "price": 49.99,
#             "stock": 5,
#             "seller": self.seller.id,
#             "category": self.category.id,
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Product.objects.count(), 2)
#         self.assertEqual(Product.objects.get(id=response.data['id']).name, "New Product")
