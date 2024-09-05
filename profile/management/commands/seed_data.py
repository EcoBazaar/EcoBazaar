from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profile.models import Customer, Seller, Address
from shop.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = 'Seed the database with dummy customers, sellers, and products'

    def handle(self, *args, **kwargs):
        # Create dummy addresses
        address1 = Address.objects.create(
            street="123 Elm Street",
            postal_code="12345",
            phone_number="+4934567890",
            city="Beerlin"
        )
        address2 = Address.objects.create(
            street="456 Oak Avenue",
            postal_code="67890",
            phone_number="+0497654321",
            city="Hamburg"
        )

        # Create dummy users for customers and sellers
        user1 = User.objects.create_user(
            username="customer1", email="customer1@example.com", password="password123"
        )
        user2 = User.objects.create_user(
            username="seller1", email="seller1@example.com", password="password123"
        )

        # Create dummy customers and sellers
        customer = Customer.objects.create(user=user1, address=address1)
        seller = Seller.objects.create(user=user2, address=address2)

        # Create a dummy category
        category1 = Category.objects.create(
            name="Electronics", description="All electronic products")
        category2 = Category.objects.create(
            name="Furniture", description="All electronic products")

        # Create dummy products
        product1 = Product.objects.create(
            name="Smartphone",
            price=699.99,
            description="A high-end smartphone",
            is_new=True,
            stock=50,
            seller=seller,
            category=category1
        )
        product2 = Product.objects.create(
            name="Laptop",
            price=700.99,
            description="A powerful laptop for professionals",
            is_new=False,
            stock=1,
            seller=seller,
            category=category1
        )
        product2 = Product.objects.create(
            name="Lunch table",
            price=250,
            description="A nice table",
            is_new=False,
            stock=1,
            seller=seller,
            category=category2
        )

        # Create dummy product images
        ProductImage.objects.create(
            product=product1, image_url="http://example.com/image1.jpg")
        ProductImage.objects.create(
            product=product2, image_url="http://example.com/image2.jpg")

        # msg fot terminal
        self.stdout.write(self.style.SUCCESS(
            'Dummy customers, sellers, and products have been created successfully.'))
