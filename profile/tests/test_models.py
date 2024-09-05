
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from profile.models import Customer, Seller, Address
from django.contrib.auth.models import User


class CustomerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
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

    def test_create_customer_and_get_by_id(self):

        Customer.objects.filter(user=self.user).delete()
        self.client.force_authenticate(user=self.user)
        data = {
            "user": self.user.pk,
            "address": self.address.pk
        }

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
            city="Hamburg"
        )

        updated_data = {
            "user": self.user.pk,
            "address": new_address.pk
        }

        response = self.client.put(
            self.customer_get_id_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["address_details"]["street"], "New Street")
        self.assertEqual(
            response.data["address_details"]["postal_code"], "54321")
        self.assertEqual(
            response.data["address_details"]["phone_number"], "+1684564666")
        self.assertEqual(response.data["address_details"]["city"], "Hamburg")

    def test_delete_customer(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.customer_get_id_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

    def test_create_customer_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "user": self.user.pk,
            "address": 99999
        }

        response = self.client.post(self.customer_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Customer.objects.count(), 0)


class SellerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@gmail.com"
        )
        self.user_super_user = User.objects.create_superuser(
            username="admin",
            password="adminpassword",
            email="admin@gmailcom"
        )
        self.address = Address.objects.create(
            street="Test Street",
            postal_code="12345",
            phone_number="+1684564673",
            city="Berlin",
        )
        self.seller = Seller.objects.create(
            user=self.user, address=self.address)
        self.seller_url = reverse("sellers")
        self.seller_get_id_url = reverse(
            "seller-detail", args=[self.seller.pk])

    def test_list_sellers(self):
        self.client.force_authenticate(user=self.user_super_user)
        response = self.client.get(self.seller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Seller.objects.count(), 1)

    # def test_create_seller_and_get_by_id(self):
    #     Seller.objects.filter(user=self.user).delete()
    #     self.client.force_authenticate(user=self.user)
    #     data = {
    #         "user": self.user.pk,
    #         "address": self.address.pk
    #     }

    #     response = self.client.post(self.seller_url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Seller.objects.count(), 1)
    #     self.assertEqual(Seller.objects.get().user, self.user)
