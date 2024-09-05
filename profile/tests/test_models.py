from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from profile.models import Customer, Seller, Address, Cart
from django.contrib.auth.models import User


class CustomerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword",
            email="test@gmail.com"
        )
        # self.admin = User.objects.create_superuser(
        #     username="admin",
        #     password="adminpassword",
        #     email="admin@gmail.com"
        # )
        self.address = Address.objects.create(
            street="Test Street",
            postal_code="12345",
            phone_number="+1684564673",
            city="Berlin",
        )
        self.customer = Customer.objects.create(
            user=self.user, address=self.address)
        self.customer_url = reverse("customers")
        self.customer_get_id_url = reverse(
            "customer-detail", args=[self.customer.pk])

    def test_get_customer_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Customer.objects.count(), 1)

    def test_get_customer_by_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.customer_get_id_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.pk)

    def test_create_customer_by_id(self):

        Customer.objects.filter(user=self.user).delete()
        self.client.force_authenticate(user=self.user)
        data = {"user": self.user.pk, "address": self.address.pk}

        response = self.client.post(self.customer_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().user, self.user)

    def test_update_customer_address(self):
        self.client.force_authenticate(user=self.user)

        new_address = Address.objects.create(
            street="New Street",
            postal_code="54321",
            phone_number="+1684564666",
            city="Hamburg",
        )

        updated_data = {"user": self.user.pk, "address": new_address.pk}

        response = self.client.put(
            self.customer_get_id_url, updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["address_details"]["street"], "New Street")
        self.assertEqual(
            response.data["address_details"]["postal_code"], "54321")
        self.assertEqual(
            response.data["address_details"]["phone_number"], "+1684564666"
        )
        self.assertEqual(response.data["address_details"]["city"], "Hamburg")

    def test_delete_customer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.customer_get_id_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

    def test_create_customer_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {"user": self.user.pk, "address": 99999}

        response = self.client.post(self.customer_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Customer.objects.count(), 0)


class SellerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword",
            email="test@gmail.com"
        )
        self.user_super_user = User.objects.create_superuser(
            username="admin", password="adminpassword",
            email="admin@gmailcom"
        )
        self.address = Address.objects.create(
            street="Test Street",
            postal_code="12345",
            phone_number="+1684564673",
            city="Berlin",
        )
        self.user_seller = Seller.objects.create(
            user=self.user, address=self.address)
        self.seller_url = reverse("sellers")
        self.seller_get_id_url = reverse(
            "seller-detail", args=[self.user_seller.pk])

    def test_list_sellers(self):
        self.client.force_authenticate(user=self.user_super_user)
        response = self.client.get(self.seller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Seller.objects.count(), 1)

    def test_seller_and_get_by_id(self):
        self.client.force_authenticate(user=self.user_seller.user)
        response = self.client.get(self.seller_get_id_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Seller.objects.count(), 1)
        self.assertEqual(Seller.objects.get().user, self.user_seller.user)

    def test_update_seller_address(self):
        self.client.force_authenticate(user=self.user_seller.user)
        new_address = Address.objects.create(
            street="Bremen Street",
            postal_code="54321",
            phone_number="+1684564777",
            city="Bremen",
        )

        updated_data = {"user": self.user.pk, "address": new_address.pk}

        response = self.client.put(
            self.seller_get_id_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["address_details"]["street"], "Bremen Street")
        self.assertEqual(
            response.data["address_details"]["postal_code"], "54321")
        self.assertEqual(
            response.data["address_details"]["phone_number"], "+1684564777"
        )
        self.assertEqual(response.data["address_details"]["city"], "Bremen")

    def test_delete_seller(self):
        self.client.force_authenticate(user=self.user_seller.user)
        response = self.client.delete(self.seller_get_id_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Seller.objects.count(), 0)


# class OrderTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="testuser",
#             password="testpassword",
#             email="test@gmail.com"
#         )
#         self.address = Address.objects.create(
#             street="Test Street",
#             postal_code="12345",
#             phone_number="+1684564673",
#             city="Berlin",
#         )
#         self.customer = Customer.objects.create(
#             user=self.user, address=self.address)
#         self.cart = Cart.objects.create(customer=self.customer)
#         self.order = Order.objects.create(cart=self.cart)


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword",
            email="test@gmail.com"
        )
        self.address = Address.objects.create(
            street="Test Street",
            postal_code="12345",
            phone_number="+1684564673",
            city="Berlin",
        )
        self.user_super_user = User.objects.create_superuser(
            username="admin", password="adminpassword", email="admin@gmailcom"
        )
        self.customer = Customer.objects.create(
            user=self.user, address=self.address)
        self.cart = Cart.objects.create(customer=self.customer)
        self.cart_url = reverse("carts", args=[self.customer.pk])
        self.cart_detail_url = reverse(
            "carts-detail", args=[self.customer.pk, self.cart.pk]
        )

    def test_get_cart_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.count(), 1)

    def test_create_cart(self):
        Cart.objects.filter(customer=self.customer).delete()
        self.client.force_authenticate(user=self.user)
        data = {"customer": self.customer.pk}
        response = self.client.post(self.cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(Cart.objects.get().customer, self.customer)

    def test_retrieve_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["customer"], self.customer.pk)
